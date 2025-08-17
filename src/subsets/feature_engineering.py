import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.subsets.brute_force import prepare_data
import pandas as pd
import numpy as np


def generate_candidates(transactions, targets):
    """
    Generate all possible transaction-target pairs (cross join)
    using the unique IDs from prepare_data().
    
    Args:
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        
    Returns:
        DataFrame: Candidate pairs with transaction and target indices and IDs
    """
    transactions = transactions.reset_index(drop=True)
    targets = targets.reset_index(drop=True)

    transactions['Transaction Index'] = transactions.index
    targets['Target Index'] = targets.index

    # Rename before merge to keep IDs distinct
    transactions = transactions.rename(columns={"Transaction ID": "Transaction Identifier"})
    targets = targets.rename(columns={"Target ID": "Target Identifier"})

    transactions['key'] = 1
    targets['key'] = 1

    candidate_pairs = pd.merge(transactions, targets, on='key')
    candidate_pairs.drop(columns='key', inplace=True)

    # Select only the four columns we need
    candidates_df = candidate_pairs[[
        'Transaction Index',
        'Target Index',
        'Transaction Identifier',
        'Target Identifier'
    ]]

    return candidates_df


def feature_engineering(candidates_df, transactions, targets):
    """
    Build features for each candidate transaction-target pair.
    
    Features:
      - amount_diff: transaction - target
      - abs_amount_diff: absolute difference
      - rel_diff: abs_diff / (abs(target) + eps)
      - txn_amount, targ_amount: original amounts
      - fuzzy_amount_str_sim: string similarity between amounts
      
    Args:
        candidates_df: DataFrame with candidate pairs
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        
    Returns:
        DataFrame: Features for each candidate pair
    """
    eps = 1e-9
    rows = []

    for _, r in candidates_df.iterrows():
        # Get row indices from candidates
        ti = int(r['Transaction Index'])
        gi = int(r['Target Index'])

        # Get amounts - detect amount columns dynamically
        trans_amount_col = [col for col in transactions.columns if 'amount' in col.lower()][0]
        targ_amount_col = [col for col in targets.columns if 'amount' in col.lower()][0]

        txn_amt = float(transactions.at[ti, trans_amount_col])
        targ_amt = float(targets.at[gi, targ_amount_col])

        # Numeric features
        amount_diff = txn_amt - targ_amt
        abs_amount_diff = abs(amount_diff)
        rel_diff = abs_amount_diff / (abs(targ_amt) + eps)

        # Append feature row
        rows.append({
            'Target Index': gi,
            'Transaction Index': ti,
            'trans_amount': txn_amt,
            'targ_amount': targ_amt,
            'amount_diff': amount_diff,
            'abs_amount_diff': abs_amount_diff,
            'rel_diff': rel_diff,
        })

    # Convert to DataFrame
    feat_df = pd.DataFrame(rows)
    return feat_df


def create_advanced_features(transactions, targets, candidates_df=None):
    """
    Create advanced features for machine learning approaches.
    
    Args:
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        candidates_df: Optional pre-generated candidates
        
    Returns:
        DataFrame: Advanced features for ML models
    """
    if candidates_df is None:
        candidates_df = generate_candidates(transactions, targets)
    
    # Basic features
    basic_features = feature_engineering(candidates_df, transactions, targets)
    
    # Advanced features
    advanced_features = []
    
    for _, row in basic_features.iterrows():
        ti = int(row['Transaction Index'])
        gi = int(row['Target Index'])
        
        # Get original data
        trans_row = transactions.iloc[ti]
        target_row = targets.iloc[gi]
        
        # Amount-based features
        trans_amt = row['trans_amount']
        target_amt = row['targ_amount']
        
        # Ratio features
        amount_ratio = trans_amt / (target_amt + 1e-9)
        log_amount_ratio = np.log(abs(amount_ratio) + 1e-9)
        
        # Distance features
        euclidean_dist = np.sqrt(trans_amt**2 + target_amt**2)
        manhattan_dist = abs(trans_amt) + abs(target_amt)
        
        # Statistical features (if we have multiple transactions)
        if len(transactions) > 1:
            trans_mean = transactions['amount'].mean()
            trans_std = transactions['amount'].std()
            trans_median = transactions['amount'].median()
            
            # Z-score features
            trans_zscore = (trans_amt - trans_mean) / (trans_std + 1e-9)
            target_zscore = (target_amt - trans_mean) / (trans_std + 1e-9)
        else:
            trans_zscore = 0
            target_zscore = 0
        
        # Categorical features (if available)
        trans_desc = str(trans_row.get('Description', ''))
        target_ref = str(target_row.get('Reference', ''))
        
        # Text similarity features
        desc_similarity = calculate_text_similarity(trans_desc, target_ref)
        
        # Combine all features
        feature_dict = {
            'Target Index': gi,
            'Transaction Index': ti,
            'trans_amount': trans_amt,
            'targ_amount': target_amt,
            'amount_diff': row['amount_diff'],
            'abs_amount_diff': row['abs_amount_diff'],
            'rel_diff': row['rel_diff'],
            'amount_ratio': amount_ratio,
            'log_amount_ratio': log_amount_ratio,
            'euclidean_dist': euclidean_dist,
            'manhattan_dist': manhattan_dist,
            'trans_zscore': trans_zscore,
            'target_zscore': target_zscore,
            'desc_similarity': desc_similarity,
            'is_exact_match': 1.0 if abs(trans_amt - target_amt) < 1e-6 else 0.0,
            'is_close_match': 1.0 if abs(trans_amt - target_amt) < 0.01 else 0.0
        }
        
        advanced_features.append(feature_dict)
    
    return pd.DataFrame(advanced_features)


def calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two text strings using multiple methods.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        float: Similarity score between 0 and 1
    """
    if not text1 or not text2 or text1.strip() == '' or text2.strip() == '':
        return 0.0
    
    # Clean and normalize text
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    
    # Exact match
    if text1 == text2:
        return 1.0
    
    # Jaccard similarity (word-based)
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if len(words1) == 0 and len(words2) == 0:
        return 1.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    jaccard_sim = len(intersection) / len(union) if len(union) > 0 else 0.0
    
    # Character-based similarity (simple)
    char_sim = 0.0
    if len(text1) > 0 and len(text2) > 0:
        common_chars = sum(1 for c in text1 if c in text2)
        char_sim = common_chars / max(len(text1), len(text2))
    
    # Substring similarity
    substring_sim = 0.0
    shorter = text1 if len(text1) < len(text2) else text2
    longer = text2 if len(text1) < len(text2) else text1
    
    if len(shorter) > 0:
        if shorter in longer:
            substring_sim = len(shorter) / len(longer)
    
    # Combined similarity score
    combined_score = (jaccard_sim * 0.5) + (char_sim * 0.3) + (substring_sim * 0.2)
    
    return combined_score


def prepare_ml_dataset(transactions, targets, feature_type='basic'):
    """
    Prepare a complete dataset for machine learning models.
    
    Args:
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        feature_type: 'basic' or 'advanced'
        
    Returns:
        tuple: (features_df, labels_df, candidates_df)
    """
    # Generate candidates
    candidates_df = generate_candidates(transactions, targets)
    
    # Generate features
    if feature_type == 'advanced':
        features_df = create_advanced_features(transactions, targets, candidates_df)
    else:
        features_df = feature_engineering(candidates_df, transactions, targets)
    
    # Create labels (1 if exact match, 0 otherwise)
    labels = []
    for _, row in features_df.iterrows():
        if 'amount_diff' in row:
            # Exact match within small tolerance
            is_match = abs(row['amount_diff']) < 1e-6
            labels.append(1.0 if is_match else 0.0)
        else:
            labels.append(0.0)
    
    labels_df = pd.DataFrame({'match_label': labels})
    
    return features_df, labels_df, candidates_df


if __name__ == '__main__':
    # Test with sample data
    try:
        transactions_file = "data/sample/Customer_Ledger_Entries_FULL.xlsx"
        targets_file = "data/sample/KH_Bank.XLSX"

        if os.path.exists(transactions_file) and os.path.exists(targets_file):
            # Load and prepare data
            trans_df, target_df = prepare_data(transactions_file, targets_file)
            
            # Limit for quick testing
            trans_df = trans_df.head(10)
            target_df = target_df.head(3)
            
            # Generate candidates and features
            candidates_df = generate_candidates(trans_df, target_df)
            features_df = feature_engineering(candidates_df, trans_df, target_df)
            
            print("Basic Features:")
            print(features_df.head())
            
            # Advanced features
            advanced_features = create_advanced_features(trans_df, target_df)
            print("\nAdvanced Features:")
            print(advanced_features.head())
            
            # ML dataset
            features_ml, labels_ml, candidates_ml = prepare_ml_dataset(trans_df, target_df, 'advanced')
            print(f"\nML Dataset Shape: {features_ml.shape}")
            print(f"Labels Shape: {labels_ml.shape}")
            print(f"Candidates Shape: {candidates_ml.shape}")
            
        else:
            print("Data files not found. Please ensure the files exist in the data/sample directory.")
            
    except Exception as e:
        print(f"Error running feature engineering: {e}")
        import traceback
        traceback.print_exc() 