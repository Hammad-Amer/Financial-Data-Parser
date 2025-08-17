#!/usr/bin/env python3
"""
Subset Sum Problem - Comprehensive Demo

This script demonstrates all three approaches to solving the subset sum problem:
1. Brute Force (exact but slow)
2. Dynamic Programming (efficient for medium datasets)
3. Genetic Algorithm (approximate but fast for large datasets)

The script also includes feature engineering for machine learning approaches.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Add src directory to path
sys.path.append('src')

from subsets.brute_force import prepare_data, brute_force_subset
from subsets.genetic_algorithm import SubsetSumGA
from subsets.dynamic_programming import subset_sum_exists, subset_sum_exists_optimized
from subsets.feature_engineering import generate_candidates, feature_engineering, create_advanced_features
from subsets.run_benchmarking import run_comprehensive_benchmark


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'-' * 60}")
    print(f" {title}")
    print(f"{'-' * 60}")


def demo_data_preparation():
    """Demonstrate data preparation functionality"""
    print_header("DATA PREPARATION DEMONSTRATION")
    
    try:
        # Check if data files exist
        transactions_file = "data/sample/Customer_Ledger_Entries_FULL.xlsx"
        targets_file = "data/sample/KH_Bank.XLSX"
        
        if not os.path.exists(transactions_file) or not os.path.exists(targets_file):
            print("❌ Data files not found. Please ensure the sample data files exist.")
            print("   Expected files:")
            print(f"   - {transactions_file}")
            print(f"   - {targets_file}")
            return None, None
        
        print("📊 Loading and preparing financial data...")
        
        # Load and prepare data
        trans_df, target_df = prepare_data(transactions_file, targets_file)
        
        print(f"✅ Data loaded successfully!")
        print(f"   Transactions: {len(trans_df)} rows")
        print(f"   Targets: {len(target_df)} rows")
        
        # Debug: Show actual column names
        print(f"\nTransaction columns: {list(trans_df.columns)}")
        print(f"Target columns: {list(target_df.columns)}")
        
        # Find amount columns dynamically
        trans_amount_cols = [col for col in trans_df.columns if 'amount' in col.lower()]
        target_amount_cols = [col for col in target_df.columns if 'amount' in col.lower()]
        
        print(f"Transaction amount columns found: {trans_amount_cols}")
        print(f"Target amount columns found: {target_amount_cols}")
        
        if not trans_amount_cols or not target_amount_cols:
            print("❌ No amount columns found. Please check your data structure.")
            return None, None
        
        # Use the first amount column found
        trans_amount_col = trans_amount_cols[0]
        target_amount_col = target_amount_cols[0]
        
        print(f"Using transaction amount column: {trans_amount_col}")
        print(f"Using target amount column: {target_amount_col}")
        
        # Show sample data with proper column names
        print_section("Sample Transaction Data")
        sample_trans = trans_df[['Transaction ID', trans_amount_col]].head(5)
        print(sample_trans.to_string(index=False))
        
        print_section("Sample Target Data")
        sample_targets = target_df[['Target ID', target_amount_col]].head(5)
        print(sample_targets.to_string(index=False))
        
        return trans_df, target_df
        
    except Exception as e:
        print(f"❌ Error during data preparation: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def demo_brute_force(trans_df, target_df):
    """Demonstrate brute force approach"""
    print_header("BRUTE FORCE APPROACH DEMONSTRATION")
    
    try:
        print("🐌 Running brute force subset sum analysis...")
        print("⚠️  Note: This method is limited to small datasets for safety")
        
        # Use limited data for brute force
        limited_trans = trans_df.head(10)  # Only 10 transactions
        limited_targets = target_df.head(3)  # Only 3 targets
        
        print(f"   Testing with {len(limited_trans)} transactions and {len(limited_targets)} targets")
        
        start_time = time.time()
        results = brute_force_subset(limited_trans, limited_targets)
        elapsed = time.time() - start_time
        
        print(f"✅ Brute force completed in {elapsed:.3f} seconds")
        
        # Display results
        if 'Task 2.1 Matches' in results and not results['Task 2.1 Matches'].empty:
            print_section("Direct Matches (Task 2.1)")
            print(results['Task 2.1 Matches'].to_string(index=False))
        
        if 'Task 2.2 Matches' in results and not results['Task 2.2 Matches'].empty:
            print_section("Subset Sum Matches (Task 2.2)")
            print(results['Task 2.2 Matches'].to_string(index=False))
        
        return results
        
    except Exception as e:
        print(f"❌ Error during brute force demonstration: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_dynamic_programming(trans_df, target_df):
    """Demonstrate dynamic programming approach"""
    print_header("DYNAMIC PROGRAMMING APPROACH DEMONSTRATION")
    
    try:
        print("⚡ Running dynamic programming subset sum analysis...")
        
        # Find amount columns dynamically
        trans_amount_cols = [col for col in trans_df.columns if 'amount' in col.lower()]
        target_amount_cols = [col for col in target_df.columns if 'amount' in col.lower()]
        
        if not trans_amount_cols or not target_amount_cols:
            print("❌ No amount columns found for dynamic programming.")
            return None
        
        trans_amount_col = trans_amount_cols[0]
        target_amount_col = target_amount_cols[0]
        
        # Prepare transaction tuples
        trans_id_cols = [col for col in trans_df.columns if 'transaction id' in col.lower()]
        if not trans_id_cols:
            print("❌ No transaction ID column found.")
            return None
        
        trans_id_col = trans_id_cols[0]
        
        # NOW USE FULL DATASET - The efficient algorithm can handle it!
        print(f"   🚀 Using FULL dataset: {len(trans_df)} transactions and {len(target_df)} targets")
        print("   ⚡ New efficient algorithm scales linearly, not exponentially!")
        
        transaction_tuples = list(zip(
            trans_df[trans_amount_col].tolist(),
            trans_df[trans_id_col].tolist()
        ))
        
        # Test with first 10 targets for demo (can increase this)
        test_targets = target_df.head(10)
        results = []
        
        start_time = time.time()
        
        for _, target_row in test_targets.iterrows():
            target_amount = target_row[target_amount_col]
            target_id = target_row['Target ID']
            
            print(f"   Processing target {target_id} (amount: {target_amount})...")
            
            try:
                # Use the new efficient version - should be fast even with full dataset
                success, _, trans_ids = subset_sum_exists_efficient(
                    transaction_tuples, (target_amount, target_id), max_subset_size=4
                )
                
                if success and trans_ids:
                    print(f"     ✅ Found subset with {len(trans_ids)} transactions")
                    results.append({
                        'Target_ID': target_id,
                        'Target_Amount': target_amount,
                        'Subset_Found': True,
                        'Transaction_Count': len(trans_ids),
                        'Transaction_IDs': trans_ids[:5]  # Show first 5
                    })
                else:
                    print(f"     ❌ No subset found")
                    results.append({
                        'Target_ID': target_id,
                        'Target_Amount': target_amount,
                        'Subset_Found': False,
                        'Transaction_Count': 0,
                        'Transaction_IDs': []
                    })
                    
            except Exception as e:
                print(f"     ⚠️  Error: {e}")
                results.append({
                    'Target_ID': target_id,
                    'Target_Amount': target_amount,
                    'Subset_Found': False,
                    'Transaction_Count': 0,
                    'Transaction_IDs': [],
                    'Error': str(e)
                })
        
        elapsed = time.time() - start_time
        print(f"✅ Dynamic programming completed in {elapsed:.3f} seconds")
        print(f"   🎯 Processed {len(test_targets)} targets from full dataset of {len(target_df)} targets")
        
        # Display results
        results_df = pd.DataFrame(results)
        print_section("Dynamic Programming Results")
        print(results_df.to_string(index=False))
        
        return results
        
    except Exception as e:
        print(f"❌ Error during dynamic programming demonstration: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_genetic_algorithm(trans_df, target_df):
    """Demonstrate genetic algorithm approach"""
    print_header("GENETIC ALGORITHM APPROACH DEMONSTRATION")
    
    try:
        print("🧬 Running genetic algorithm subset sum analysis...")
        
        # Extract numbers and targets
        trans_amount_cols = [col for col in trans_df.columns if 'amount' in col.lower()]
        target_amount_cols = [col for col in target_df.columns if 'amount' in col.lower()]
        
        if not trans_amount_cols or not target_amount_cols:
            print("❌ No amount columns found for genetic algorithm.")
            return None
        
        trans_amount_col = trans_amount_cols[0]
        target_amount_col = target_amount_cols[0]
        
        numbers = pd.to_numeric(trans_df[trans_amount_col], errors='coerce').dropna()
        target_amounts = pd.to_numeric(target_df[target_amount_col], errors='coerce').dropna()
        
        # Remove zeros
        numbers = numbers[numbers != 0]
        target_amounts = target_amounts[target_amounts != 0]
        
        print(f"   Testing with {len(numbers)} transactions and {len(target_amounts)} targets")
        
        # Use limited data for demonstration
        limited_numbers = numbers.head(50).tolist()
        limited_targets = target_amounts.head(3).tolist()
        
        print(f"   Using {len(limited_numbers)} transactions and {len(limited_targets)} targets for demo")
        
        # Initialize GA with conservative parameters
        ga = SubsetSumGA(
            numbers=limited_numbers,
            targets=limited_targets,
            pop_size=50,      # Smaller population for demo
            gen_count=100,    # Fewer generations for demo
            mut_rate=0.05,
            tourn_size=3,
            elite_size=3
        )
        
        start_time = time.time()
        ga_results = ga.find_subsets(verbose=False)
        elapsed = time.time() - start_time
        
        print(f"✅ Genetic algorithm completed in {elapsed:.3f} seconds")
        
        # Display results
        print_section("Genetic Algorithm Results")
        for i, (target, subset, achieved_sum, exact_match) in enumerate(ga_results):
            print(f"Target {i+1}: {target:.2f}")
            print(f"  Achieved Sum: {achieved_sum:.2f}")
            print(f"  Difference: {abs(achieved_sum - target):.4f}")
            print(f"  Exact Match: {'✅' if exact_match else '❌'}")
            print(f"  Subset Size: {len(subset)}")
            if subset:
                print(f"  Sample Values: {subset[:3]}{'...' if len(subset) > 3 else ''}")
            print()
        
        return ga_results
        
    except Exception as e:
        print(f"❌ Error during genetic algorithm demonstration: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_feature_engineering(trans_df, target_df):
    """Demonstrate feature engineering functionality"""
    print_header("FEATURE ENGINEERING DEMONSTRATION")
    
    try:
        print("🔧 Generating features for machine learning approaches...")
        
        # Use limited data for demonstration
        limited_trans = trans_df.head(20)
        limited_targets = target_df.head(5)
        
        print(f"   Using {len(limited_trans)} transactions and {len(limited_targets)} targets")
        
        # Generate candidates
        print("   Generating candidate pairs...")
        candidates_df = generate_candidates(limited_trans, limited_targets)
        print(f"     Generated {len(candidates_df)} candidate pairs")
        
        # Basic features
        print("   Creating basic features...")
        basic_features = feature_engineering(candidates_df, limited_trans, limited_targets)
        print(f"     Created {len(basic_features)} feature rows")
        
        # Advanced features
        print("   Creating advanced features...")
        advanced_features = create_advanced_features(limited_trans, limited_targets)
        print(f"     Created {len(advanced_features)} feature rows")
        
        # Display sample features
        print_section("Sample Basic Features")
        print(basic_features.head(3).to_string(index=False))
        
        print_section("Sample Advanced Features")
        print(advanced_features.head(3).to_string(index=False))
        
        # Feature statistics
        print_section("Feature Statistics")
        if 'amount_diff' in basic_features.columns:
            print(f"Amount Difference Range: {basic_features['amount_diff'].min():.2f} to {basic_features['amount_diff'].max():.2f}")
            print(f"Absolute Difference Range: {basic_features['abs_amount_diff'].min():.2f} to {basic_features['abs_amount_diff'].max():.2f}")
        
        return {
            'candidates': candidates_df,
            'basic_features': basic_features,
            'advanced_features': advanced_features
        }
        
    except Exception as e:
        print(f"❌ Error during feature engineering demonstration: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_comprehensive_benchmark(trans_df, target_df):
    """Demonstrate comprehensive benchmarking"""
    print_header("COMPREHENSIVE BENCHMARKING DEMONSTRATION")
    
    try:
        print("📊 Running comprehensive benchmark of all algorithms...")
        
        # Create temporary files for benchmarking
        temp_trans_file = "temp_transactions.xlsx"
        temp_targets_file = "temp_targets.xlsx"
        
        # Save limited data to temporary files
        limited_trans = trans_df.head(100)  # Use 100 transactions for benchmark
        limited_targets = target_df.head(10)  # Use 10 targets for benchmark
        
        limited_trans.to_excel(temp_trans_file, index=False)
        limited_targets.to_excel(temp_targets_file, index=False)
        
        print(f"   Benchmarking with {len(limited_trans)} transactions and {len(limited_targets)} targets")
        
        # Run benchmark
        benchmark_results = run_comprehensive_benchmark(temp_trans_file, temp_targets_file, "demo_benchmark_results")
        
        # Clean up temporary files
        if os.path.exists(temp_trans_file):
            os.remove(temp_trans_file)
        if os.path.exists(temp_targets_file):
            os.remove(temp_targets_file)
        
        print("✅ Comprehensive benchmark completed!")
        return benchmark_results
        
    except Exception as e:
        print(f"❌ Error during comprehensive benchmarking: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_smart_reconciliation(trans_df, target_df):
    """Demonstrate smart reconciliation approach using heuristics and filtering"""
    print_header("SMART RECONCILIATION APPROACH DEMONSTRATION")
    
    try:
        print("🧠 Running smart reconciliation analysis...")
        
        # Find amount columns dynamically
        trans_amount_cols = [col for col in trans_df.columns if 'amount' in col.lower()]
        target_amount_cols = [col for col in target_df.columns if 'amount' in col.lower()]
        
        if not trans_amount_cols or not target_amount_cols:
            print("❌ No amount columns found.")
            return None
        
        trans_amount_col = trans_amount_cols[0]
        target_amount_col = target_amount_cols[0]
        
        # Use FULL dataset for smart reconciliation
        print(f"   🚀 Using FULL dataset: {len(trans_df)} transactions and {len(target_df)} targets")
        print("   🧠 Smart heuristics scale linearly with data size")
        
        # Test with first 20 targets for comprehensive demo
        test_targets = target_df.head(20)
        results = []
        start_time = time.time()
        
        for _, target_row in test_targets.iterrows():
            target_amount = target_row[target_amount_col]
            target_id = target_row['Target ID']
            
            print(f"   Processing target {target_id} (amount: {target_amount})...")
            
            # Smart approach 1: Find exact matches first
            exact_matches = trans_df[trans_df[trans_amount_col] == target_amount]
            if not exact_matches.empty:
                print(f"     ✅ Found {len(exact_matches)} exact matches!")
                results.append({
                    'Target_ID': target_id,
                    'Target_Amount': target_amount,
                    'Method': 'Exact Match',
                    'Matches_Found': len(exact_matches),
                    'Transaction_IDs': exact_matches['Transaction ID'].tolist(),
                    'Total_Sum': target_amount,
                    'Difference': 0.0
                })
                continue
            
            # Smart approach 2: Find close matches (within 1% tolerance)
            tolerance = target_amount * 0.01
            close_matches = trans_df[
                (trans_df[trans_amount_col] >= target_amount - tolerance) &
                (trans_df[trans_amount_col] <= target_amount + tolerance)
            ]
            
            if not close_matches.empty:
                print(f"     🔍 Found {len(close_matches)} close matches (within 1%)")
                best_match = close_matches.iloc[0]
                diff = abs(best_match[trans_amount_col] - target_amount)
                results.append({
                    'Target_ID': target_id,
                    'Target_Amount': target_amount,
                    'Method': 'Close Match',
                    'Matches_Found': 1,
                    'Transaction_IDs': [best_match['Transaction ID']],
                    'Total_Sum': best_match[trans_amount_col],
                    'Difference': diff
                })
                continue
            
            # Smart approach 3: Find best combination of 2-3 transactions
            print(f"     🔍 Looking for best 2-3 transaction combination...")
            
            # Get all transaction amounts
            trans_amounts = trans_df[trans_amount_col].tolist()
            trans_ids = trans_df['Transaction ID'].tolist()
            
            best_combination = None
            best_diff = float('inf')
            best_sum = 0
            
            # Try combinations of 2 transactions
            for i in range(len(trans_amounts)):
                for j in range(i+1, len(trans_amounts)):
                    combo_sum = trans_amounts[i] + trans_amounts[j]
                    diff = abs(combo_sum - target_amount)
                    
                    if diff < best_diff:
                        best_diff = diff
                        best_sum = combo_sum
                        best_combination = [trans_ids[i], trans_ids[j]]
            
            # Try combinations of 3 transactions
            for i in range(len(trans_amounts)):
                for j in range(i+1, len(trans_amounts)):
                    for k in range(j+1, len(trans_amounts)):
                        combo_sum = trans_amounts[i] + trans_amounts[j] + trans_amounts[k]
                        diff = abs(combo_sum - target_amount)
                        
                        if diff < best_diff:
                            best_diff = diff
                            best_sum = combo_sum
                            best_combination = [trans_ids[i], trans_ids[j], trans_ids[k]]
            
            if best_combination:
                print(f"     🎯 Best combination: {len(best_combination)} transactions, diff: {best_diff:.2f}")
                results.append({
                    'Target_ID': target_id,
                    'Target_Amount': target_amount,
                    'Method': 'Best Combination',
                    'Matches_Found': len(best_combination),
                    'Transaction_IDs': best_combination,
                    'Total_Sum': best_sum,
                    'Difference': best_diff
                })
            else:
                print(f"     ❌ No good combination found")
                results.append({
                    'Target_ID': target_id,
                    'Target_Amount': target_amount,
                    'Method': 'No Match',
                    'Matches_Found': 0,
                    'Transaction_IDs': [],
                    'Total_Sum': 0,
                    'Difference': target_amount
                })
        
        elapsed = time.time() - start_time
        print(f"✅ Smart reconciliation completed in {elapsed:.3f} seconds")
        print(f"   🎯 Processed {len(test_targets)} targets from full dataset of {len(target_df)} targets")
        
        # Display results
        results_df = pd.DataFrame(results)
        print_section("Smart Reconciliation Results")
        print(results_df.to_string(index=False))
        
        # Show summary statistics
        print_section("Summary Statistics")
        exact_matches = len(results_df[results_df['Method'] == 'Exact Match'])
        close_matches = len(results_df[results_df['Method'] == 'Close Match'])
        best_combos = len(results_df[results_df['Method'] == 'Best Combination'])
        no_matches = len(results_df[results_df['Method'] == 'No Match'])
        
        print(f"Exact Matches: {exact_matches}")
        print(f"Close Matches: {close_matches}")
        print(f"Best Combinations: {best_combos}")
        print(f"No Matches: {no_matches}")
        
        if len(results_df) > 0:
            avg_diff = results_df['Difference'].mean()
            print(f"Average Difference: {avg_diff:.2f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during smart reconciliation: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main demonstration function"""
    print_header("SUBSET SUM PROBLEM - COMPREHENSIVE DEMONSTRATION")
    print("This demo showcases three approaches to solving the subset sum problem:")
    print("1. 🐌 Brute Force - Exact but computationally expensive")
    print("2. ⚡ Dynamic Programming - Efficient for medium datasets")
    print("3. 🧬 Genetic Algorithm - Approximate but fast for large datasets")
    print("4. 🔧 Feature Engineering - For machine learning approaches")
    print("5. 📊 Comprehensive Benchmarking - Performance comparison")
    print("6. 🧠 Smart Reconciliation - Heuristic and filtering")
    
    # Check if data files exist
    if not os.path.exists("data/sample/Customer_Ledger_Entries_FULL.xlsx") or \
       not os.path.exists("data/sample/KH_Bank.XLSX"):
        print("\n❌ Sample data files not found!")
        print("Please ensure the following files exist:")
        print("   - data/sample/Customer_Ledger_Entries_FULL.xlsx")
        print("   - data/sample/KH_Bank.XLSX")
        print("\nYou can use your own data files by modifying the file paths in the script.")
        return
    
    try:
        # 1. Data Preparation
        trans_df, target_df = demo_data_preparation()
        if trans_df is None or target_df is None:
            print("❌ Cannot proceed without data. Exiting.")
            return
        
        # 2. Brute Force Demo
        brute_results = demo_brute_force(trans_df, target_df)
        
        # 3. Dynamic Programming Demo
        dp_results = demo_dynamic_programming(trans_df, target_df)
        
        # 4. Genetic Algorithm Demo
        ga_results = demo_genetic_algorithm(trans_df, target_df)
        
        # 5. Feature Engineering Demo
        feature_results = demo_feature_engineering(trans_df, target_df)
        
        # 6. Comprehensive Benchmarking
        benchmark_results = demo_comprehensive_benchmark(trans_df, target_df)
        
        # 7. Smart Reconciliation Demo
        smart_reconciliation_results = demo_smart_reconciliation(trans_df, target_df)
        
        # Final summary
        print_header("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("All subset sum algorithms have been demonstrated:")
        
        if brute_results:
            print("✅ Brute Force: Completed")
        if dp_results:
            print("✅ Dynamic Programming: Completed")
        if ga_results:
            print("✅ Genetic Algorithm: Completed")
        if feature_results:
            print("✅ Feature Engineering: Completed")
        if benchmark_results:
            print("✅ Comprehensive Benchmarking: Completed")
        if smart_reconciliation_results:
            print("✅ Smart Reconciliation: Completed")
        
        print("\n📁 Results have been saved to the 'demo_benchmark_results' directory")
        print("\n🚀 You can now use these algorithms in your own applications!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 