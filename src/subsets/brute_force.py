import itertools
import time
import os
import pandas as pd
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.format_parser import FormatParser


def prepare_data(transaction, target):
    """
    Prepare transaction and target data for subset sum analysis.
    
    Args:
        transaction: Path to transaction Excel file
        target: Path to target Excel file
        
    Returns:
        tuple: (processed_transactions_df, processed_targets_df)
    """
    trans_df = pd.read_excel(transaction)
    target_df = pd.read_excel(target)
    parser = FormatParser()

    # Add unique identifiers
    trans_df["Transaction ID"] = [f"TX{i+1:03}" for i in range(len(trans_df))]
    target_df["Target ID"] = [f"TG{i+1:03}" for i in range(len(target_df))]

    # Clean and parse amount columns
    for df in [trans_df, target_df]:
        for col in df.columns:
            if 'amount' in col.lower():
                # Parse amounts and extract the numeric values
                parsed_amounts = df[col].apply(lambda x: parser.parse_amount(x))
                
                # Extract the actual numeric values from the parsed dictionaries
                def extract_numeric_value(parsed_dict):
                    if isinstance(parsed_dict, dict) and 'parsed_value' in parsed_dict:
                        return parsed_dict['parsed_value']
                    elif isinstance(parsed_dict, (int, float)):
                        return parsed_dict
                    else:
                        return None
                
                df[col] = parsed_amounts.apply(extract_numeric_value)

    return trans_df, target_df


def brute_force_subset(transactions, target):
    """
    Brute force approach to find subset sum matches.
    
    Args:
        transactions: DataFrame with transaction data
        target: DataFrame with target data
        
    Returns:
        dict: Results containing direct matches and subset sum matches
    """
    start_time = time.time()

    # Find amount columns
    trans_amount_col = [col for col in transactions.columns if 'amount' in col.lower()][0]
    target_amount_col = [col for col in target.columns if 'amount' in col.lower()][0]

    direct_matches = []
    results = {}

    # Task 2.1: Direct matching between individual transactions and targets
    print("Performing Task 2.1: Direct matching...")
    for _, trans_row in transactions.iterrows():
        for _, target_rows in target.iterrows():
            if trans_row[trans_amount_col] == target_rows[target_amount_col]:
                direct_matches.append({
                    "transaction_amount": trans_row[trans_amount_col],
                    "target_amount": target_rows[target_amount_col],
                    "transaction_id": trans_row['Transaction ID'],
                    "target_id": target_rows['Target ID']
                })

    task_2_1_time = time.time() - start_time
    results['Task 2.1 Matches'] = pd.DataFrame(direct_matches)
    results['Task 2.1 Time'] = task_2_1_time

    print(f"Task 2.1 completed in {task_2_1_time:.3f} seconds")
    print(f"Found {len(direct_matches)} direct matches")

    # Task 2.2: Subset sum matching
    print("Performing Task 2.2: Subset sum matching...")
    subset_sum_matches = []

    trans_amounts = transactions[trans_amount_col].tolist()
    trans_ids = transactions['Transaction ID'].tolist()

    for _, target_row in target.iterrows():
        target_amt = target_row[target_amount_col]
        target_id = target_row['Target ID']
        found = False

        # Brute force: try all subset sizes from 1 to len(transactions)
        for r in range(1, min(len(trans_amounts) + 1, 21)):  # Limit to 20 items for performance
            for combo in itertools.combinations(range(len(trans_amounts)), r):
                combo_ids = [trans_ids[i] for i in combo]
                combo_vals = [trans_amounts[i] for i in combo]
                
                if sum(trans_amounts[i] for i in combo) == target_amt:
                    subset_sum_matches.append({
                        'Target Identifier': target_id,
                        'Matched Transactions': combo_ids,
                        'Transaction Amounts': combo_vals,
                        'Sum': target_amt,
                        'Subset Size': len(combo)
                    })
                    found = True
                    break  # Found a match for this target
            if found:
                break

    task_2_2_time = time.time() - start_time
    results['Task 2.2 Matches'] = pd.DataFrame(subset_sum_matches)
    results['Task 2.2 Time'] = task_2_2_time

    print(f"Task 2.2 completed in {task_2_2_time:.3f} seconds")
    print(f"Found {len(subset_sum_matches)} subset sum matches")

    return results


if __name__ == '__main__':
    # Test with sample data
    try:
        # Assuming data files are in the data/sample directory
        transactions_file = "data/sample/Customer_Ledger_Entries_FULL.xlsx"
        targets_file = "data/sample/KH_Bank.XLSX"

        if os.path.exists(transactions_file) and os.path.exists(targets_file):
            # Use only first few rows for testing
            trans_df, target_df = prepare_data(transactions_file, targets_file)
            chunk_trans_data = trans_df.head(10)  # Limit to 10 transactions for testing
            chunk_target_data = target_df.head(3)  # Limit to 3 targets for testing

            result = brute_force_subset(chunk_trans_data, chunk_target_data)
            print('\nResults:', result)
        else:
            print("Data files not found. Please ensure the files exist in the data/sample directory.")
            
    except Exception as e:
        print(f"Error running brute force: {e}")
        import traceback
        traceback.print_exc() 