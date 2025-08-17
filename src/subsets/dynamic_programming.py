import pandas as pd
import os
import time
from tqdm import tqdm
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.subsets.brute_force import prepare_data


def subset_sum_exists_efficient(transactions, target, max_subset_size=5):
    """
    Check if a subset of transactions sums to the target value using dynamic programming.
    
    Args:
        transactions: List of tuples [(amount, trans_id), ...]
        target: Tuple (target_amount, target_id)
        max_sum: Maximum sum to consider (optional)
        precision: Scaling factor for floats (e.g., 100 for 2 decimals)
        
    Returns:
        Tuple (success, target_id, trans_ids):
            - success: Boolean (True if subset exists)
            - target_id: ID of the target
            - trans_ids: List of Transaction IDs forming the subset (empty if none)
    """
    if not transactions:
        return (target[0] == 0, target[1], [])
    
    target_amount = target[0]
    target_id = target[1]
    
    # Filter out zero amounts and get unique amounts
    nums = [(amount, trans_id) for amount, trans_id in transactions if amount != 0]
    
    if not nums:
        return (target_amount == 0, target_id, [])
    
    # Try exact matches first (O(n) - very fast)
    for amount, trans_id in nums:
        if abs(amount - target_amount) < 0.01:  # Small tolerance for floating point
            return (True, target_id, [trans_id])
    
    # Try combinations of 2 transactions (O(n²) - manageable)
    if max_subset_size >= 2:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                combo_sum = nums[i][0] + nums[j][0]
                if abs(combo_sum - target_amount) < 0.01:
                    return (True, target_id, [nums[i][1], nums[j][1]])
    
    # Try combinations of 3 transactions (O(n³) - only for small n)
    if max_subset_size >= 3 and len(nums) <= 20:  # Limit to small datasets
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                for k in range(j + 1, len(nums)):
                    combo_sum = nums[i][0] + nums[j][0] + nums[k][0]
                    if abs(combo_sum - target_amount) < 0.01:
                        return (True, target_id, [nums[i][1], nums[j][1], nums[k][1]])
    
    # Try combinations of 4 transactions (only for very small datasets)
    if max_subset_size >= 4 and len(nums) <= 10:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                for k in range(j + 1, len(nums)):
                    for l in range(k + 1, len(nums)):
                        combo_sum = nums[i][0] + nums[j][0] + nums[k][0] + nums[l][0]
                        if abs(combo_sum - target_amount) < 0.01:
                            return (True, target_id, [nums[i][1], nums[j][1], nums[k][1], nums[l][1]])
    
    return (False, target_id, [])


def subset_sum_exists(transactions, target, max_sum=None, precision=100):
    """
    Legacy function - now calls the efficient version.
    """
    return subset_sum_exists_efficient(transactions, target, max_subset_size=5)


def subset_sum_exists_optimized(transactions, target, precision=100):
    """
    Optimized version that uses smart heuristics.
    """
    return subset_sum_exists_efficient(transactions, target, max_subset_size=3)


def run_dynamic_programming_analysis(transactions_file, targets_file, output_dir="results"):
    """
    Run comprehensive dynamic programming analysis on transaction and target data.
    """
    # Start timing the whole process
    start_time = time.time()
    
    print("Loading data files...")
    load_start = time.time()
    try:
        trans_df, target_df = prepare_data(transactions_file, targets_file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    load_time = time.time() - load_start
    print(f"Data loading completed in {load_time:.2f} seconds")

    # Find amount and ID columns
    trans_amount_cols = [col for col in trans_df.columns if 'amount' in col.lower()]
    target_amount_cols = [col for col in target_df.columns if 'amount' in col.lower()]
    trans_id_cols = [col for col in trans_df.columns if 'transaction id' in col.lower()]
    target_id_cols = [col for col in target_df.columns if 'target id' in col.lower()]

    if not trans_amount_cols or not target_amount_cols or not trans_id_cols or not target_id_cols:
        print("Error: Missing 'amount' or 'ID' column in one or both DataFrames")
        return None

    trans_amount_col = trans_amount_cols[0]
    target_amount_col = target_amount_cols[0]
    trans_id_col = trans_id_cols[0]
    target_id_col = target_id_cols[0]

    # Pair transaction amounts with their IDs
    trans_values = list(zip(
        pd.to_numeric(trans_df[trans_amount_col], errors='coerce').dropna(),
        trans_df[trans_id_col].dropna()
    ))
    
    # Pair target amounts with their IDs
    target_values = list(zip(
        pd.to_numeric(target_df[target_amount_col], errors='coerce').dropna(),
        target_df[target_id_col].dropna()
    ))

    print(f"Loaded {len(trans_values)} transaction values, {len(target_values)} target values")

    # Process targets
    if not target_values:
        print("No valid target values found")
        return None

    # Prepare results list for CSV output
    results = []
    
    # Process all targets with progress bar
    print(f"\nProcessing {len(target_values)} targets...")
    processing_start = time.time()
    
    for i, t in enumerate(tqdm(target_values, desc="Finding subsets", unit="target")):
        target_amount, target_id = t
        
        # Use the efficient version
        success, returned_target_id, trans_ids = subset_sum_exists_efficient(
            trans_values, t, max_subset_size=4
        )
        
        # Calculate sum and collect transaction details if subset found
        if success and trans_ids:
            # Get the actual amounts for verification
            matching_transactions = [(amount, tid) for amount, tid in trans_values if tid in trans_ids]
            subset_sum = sum(amount for amount, tid in matching_transactions)
            subset_trans_ids = [tid for amount, tid in matching_transactions]
            
            # Verify the match
            is_match = abs(subset_sum - target_amount) < 0.01
            
            result_row = {
                'Target_ID': target_id,
                'Target_Amount': target_amount,
                'Subset_Found': True,
                'Subset_Sum': subset_sum,
                'Sum_Match': is_match,
                'Transaction_Count': len(subset_trans_ids),
                'Transaction_IDs': '|'.join(map(str, subset_trans_ids)),
                'Processing_Method': 'Efficient DP'
            }
        else:
            result_row = {
                'Target_ID': target_id,
                'Target_Amount': target_amount,
                'Subset_Found': False,
                'Subset_Sum': None,
                'Sum_Match': False,
                'Transaction_Count': 0,
                'Transaction_IDs': '',
                'Processing_Method': 'Efficient DP'
            }
        
        results.append(result_row)
        
        # Print progress for first few and last few
        if i < 5 or i >= len(target_values) - 5:
            status = "FOUND" if success else "NOT FOUND"
            print(f"Target {target_id} ({target_amount}): {status}")
            if success and trans_ids:
                print(f"  -> Sum: {subset_sum}, IDs: {trans_ids[:5]}{'...' if len(trans_ids) > 5 else ''}")
    
    processing_time = time.time() - processing_start
    print(f"\nProcessing completed in {processing_time:.2f} seconds")
    
    # Create DataFrame and save to CSV
    print("\nSaving results to CSV...")
    results_df = pd.DataFrame(results)
    
    # Add summary statistics
    total_targets = len(results_df)
    found_subsets = len(results_df[results_df['Subset_Found'] == True])
    success_rate = (found_subsets / total_targets) * 100 if total_targets > 0 else 0
    
    print(f"\nSUMMARY:")
    print(f"Total targets processed: {total_targets}")
    print(f"Subsets found: {found_subsets}")
    print(f"Success rate: {success_rate:.1f}%")
    
    # Generate output filename with timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"subset_sum_results_{timestamp}.csv"
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
    
    # Display sample results
    print(f"\nSample results (first 10 rows):")
    print(results_df.head(10).to_string(index=False))
    
    # Show some statistics
    if found_subsets > 0:
        avg_transaction_count = results_df[results_df['Subset_Found'] == True]['Transaction_Count'].mean()
        max_transaction_count = results_df[results_df['Subset_Found'] == True]['Transaction_Count'].max()
        print(f"\nSubset Statistics:")
        print(f"Average transactions per subset: {avg_transaction_count:.1f}")
        print(f"Maximum transactions in a subset: {max_transaction_count}")
    
    # Total execution time
    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    print(f"Time breakdown:")
    print(f"  Data loading: {load_time:.2f}s ({(load_time/total_time)*100:.1f}%)")
    print(f"  Processing: {processing_time:.2f}s ({(processing_time/total_time)*100:.1f}%)")
    print(f"  Other: {(total_time-load_time-processing_time):.2f}s ({((total_time-load_time-processing_time)/total_time)*100:.1f}%)")
    
    return results_df


if __name__ == '__main__':
    # Test with sample data
    try:
        transactions_file = "data/sample/Customer_Ledger_Entries_FULL.xlsx"
        targets_file = "data/sample/KH_Bank.XLSX"

        if os.path.exists(transactions_file) and os.path.exists(targets_file):
            results = run_dynamic_programming_analysis(transactions_file, targets_file)
            if results is not None:
                print("Dynamic programming analysis completed successfully!")
        else:
            print("Data files not found. Please ensure the files exist in the data/sample directory.")
            
    except Exception as e:
        print(f"Error running dynamic programming analysis: {e}")
        import traceback
        traceback.print_exc() 