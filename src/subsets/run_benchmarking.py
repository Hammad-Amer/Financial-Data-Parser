"""
Comprehensive Benchmarking Script for Subset Sum Algorithms

This script runs all three approaches (Brute Force, Dynamic Programming, Genetic Algorithm)
and compares their performance, accuracy, and resource usage.
"""

import time
import tracemalloc
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.subsets.brute_force import prepare_data, brute_force_subset
from src.subsets.genetic_algorithm import SubsetSumGA
from src.subsets.dynamic_programming import subset_sum_exists, subset_sum_exists_optimized
from src.subsets.feature_engineering import generate_candidates, feature_engineering


def format_time(seconds):
    """Format time in human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.2f}s"


def run_brute_force_benchmark(transactions, targets, max_transactions=20, max_targets=5):
    """
    Run brute force benchmark with safety limits.
    
    Args:
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        max_transactions: Maximum number of transactions to process
        max_targets: Maximum number of targets to process
        
    Returns:
        dict: Benchmark results
    """
    print(f"🐌 Running Brute Force Benchmark...")
    print(f"  Transactions: {min(len(transactions), max_transactions)}")
    print(f"  Targets: {min(len(targets), max_targets)}")
    
    # Limit data for safety
    limited_trans = transactions.head(max_transactions).copy()
    limited_targets = targets.head(max_targets).copy()
    
    # Start monitoring
    start_time = time.time()
    tracemalloc.start()
    
    try:
        # Run brute force
        results = brute_force_subset(limited_trans, limited_targets)
        
        # Count matches
        total_matches = 0
        if 'Task 2.1 Matches' in results and not results['Task 2.1 Matches'].empty:
            total_matches += len(results['Task 2.1 Matches'])
        if 'Task 2.2 Matches' in results and not results['Task 2.2 Matches'].empty:
            total_matches += len(results['Task 2.2 Matches'])
        
        elapsed = time.time() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "Method": "Brute Force",
            "Time (s)": round(elapsed, 3),
            "Time Display": format_time(elapsed),
            "Memory (KB)": round(peak / 1024, 2),
            "Matches": total_matches,
            "Targets Tested": len(limited_targets),
            "Transactions Used": len(limited_trans),
            "Details": results,
            "Status": "Completed"
        }
        
    except Exception as e:
        tracemalloc.stop()
        elapsed = time.time() - start_time
        return {
            "Method": "Brute Force",
            "Time (s)": round(elapsed, 3),
            "Time Display": format_time(elapsed),
            "Memory (KB)": 0,
            "Matches": 0,
            "Targets Tested": len(limited_targets),
            "Transactions Used": len(limited_trans),
            "Details": {"Error": str(e)},
            "Status": f"Failed: {str(e)}"
        }


def run_dynamic_programming_benchmark(transactions, targets, precision=100, max_sum_limit=0):
    """
    Run dynamic programming benchmark.
    
    Args:
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        precision: Precision for decimal handling
        max_sum_limit: Maximum sum limit for memory management
        
    Returns:
        dict: Benchmark results
    """
    print(f"⚡ Running Dynamic Programming Benchmark...")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Targets: {len(targets)}")
    print(f"  Precision: {precision}")
    print(f"  Max Sum Limit: {'Auto' if max_sum_limit == 0 else max_sum_limit}")
    
    # Start monitoring
    start_time = time.time()
    tracemalloc.start()
    
    try:
        # Dynamically find amount and ID columns
        trans_amount_cols = [col for col in transactions.columns if 'amount' in col.lower()]
        target_amount_cols = [col for col in targets.columns if 'amount' in col.lower()]
        trans_id_cols = [col for col in transactions.columns if 'transaction id' in col.lower()]
        target_id_cols = [col for col in targets.columns if 'target id' in col.lower()]
        
        if not trans_amount_cols or not target_amount_cols or not trans_id_cols or not target_id_cols:
            raise ValueError(f"Missing required columns. Found: trans_amount={trans_amount_cols}, target_amount={target_amount_cols}, trans_id={trans_id_cols}, target_id={target_id_cols}")
        
        trans_amount_col = trans_amount_cols[0]
        target_amount_col = target_amount_cols[0]
        trans_id_col = trans_id_cols[0]
        target_id_col = target_id_cols[0]
        
        print(f"    Using columns: trans_amount={trans_amount_col}, target_amount={target_amount_col}")
        
        transaction_tuples = list(zip(
            transactions[trans_amount_col].tolist(),
            transactions[trans_id_col].tolist()
        ))
        
        # Process targets
        matches_found = 0
        for _, target_row in targets.iterrows():
            target_amount = target_row[target_amount_col]
            target_id = target_row[target_id_col]
            
            try:
                # Use optimized version first for large datasets
                if len(transaction_tuples) > 1000:
                    success, _, trans_ids = subset_sum_exists_optimized(
                        transaction_tuples, (target_amount, target_id), precision
                    )
                else:
                    success, _, trans_ids = subset_sum_exists(
                        transaction_tuples, (target_amount, target_id), 
                        max_sum=max_sum_limit if max_sum_limit > 0 else None, 
                        precision=precision
                    )
                
                if success and trans_ids:
                    matches_found += 1
                    
            except Exception as e:
                print(f"    Warning: Error processing target {target_id}: {e}")
                continue
        
        elapsed = time.time() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "Method": "Dynamic Programming",
            "Time (s)": round(elapsed, 3),
            "Time Display": format_time(elapsed),
            "Memory (KB)": round(peak / 1024, 2),
            "Matches": matches_found,
            "Targets Tested": len(targets),
            "Transactions Used": len(transactions),
            "Settings": {"Precision": precision, "Max Sum Limit": max_sum_limit},
            "Status": "Completed"
        }
        
    except Exception as e:
        tracemalloc.stop()
        elapsed = time.time() - start_time
        return {
            "Method": "Dynamic Programming",
            "Time (s)": round(elapsed, 3),
            "Time Display": format_time(elapsed),
            "Memory (KB)": 0,
            "Matches": 0,
            "Targets Tested": len(targets),
            "Transactions Used": len(transactions),
            "Settings": {"Precision": precision, "Max Sum Limit": max_sum_limit},
            "Status": f"Failed: {str(e)}"
        }


def run_genetic_algorithm_benchmark(transactions, targets, pop_size=100, gen_count=200, 
                                   mut_rate=0.05, tourn_size=3, elite_size=5):
    """
    Run genetic algorithm benchmark.
    
    Args:
        transactions: DataFrame with transaction data
        targets: DataFrame with target data
        pop_size: Population size
        gen_count: Number of generations
        mut_rate: Mutation rate
        tourn_size: Tournament size
        elite_size: Elite size
        
    Returns:
        dict: Benchmark results
    """
    print(f"🧬 Running Genetic Algorithm Benchmark...")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Targets: {len(targets)}")
    print(f"  Population: {pop_size}, Generations: {gen_count}")
    
    # Start monitoring
    start_time = time.time()
    tracemalloc.start()
    
    try:
        # Dynamically find amount columns
        trans_amount_cols = [col for col in transactions.columns if 'amount' in col.lower()]
        target_amount_cols = [col for col in targets.columns if 'amount' in col.lower()]
        
        if not trans_amount_cols or not target_amount_cols:
            raise ValueError(f"Missing amount columns. Found: trans_amount={trans_amount_cols}, target_amount={target_amount_cols}")
        
        trans_amount_col = trans_amount_cols[0]
        target_amount_col = target_amount_cols[0]
        
        print(f"    Using columns: trans_amount={trans_amount_col}, target_amount={target_amount_col}")
        
        numbers = pd.to_numeric(transactions[trans_amount_col], errors='coerce').dropna()
        target_amounts = pd.to_numeric(targets[target_amount_col], errors='coerce').dropna()
        
        # Remove zeros
        numbers = numbers[numbers != 0]
        target_amounts = target_amounts[target_amounts != 0]
        
        if len(numbers) == 0 or len(target_amounts) == 0:
            raise ValueError("No valid numbers or targets found")
        
        # Initialize GA
        ga = SubsetSumGA(
            numbers=numbers.tolist(),
            targets=target_amounts.tolist(),
            pop_size=pop_size,
            gen_count=gen_count,
            mut_rate=mut_rate,
            tourn_size=tourn_size,
            elite_size=elite_size
        )
        
        # Run GA
        ga_results = ga.find_subsets(verbose=False)
        
        # Count matches and exact matches
        total_matches = len(ga_results)
        exact_matches = sum(1 for _, _, _, exact in ga_results if exact)
        
        elapsed = time.time() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "Method": "Genetic Algorithm",
            "Time (s)": round(elapsed, 3),
            "Time Display": format_time(elapsed),
            "Memory (KB)": round(peak / 1024, 2),
            "Matches": total_matches,
            "Exact Matches": exact_matches,
            "Targets Tested": len(target_amounts),
            "Transactions Used": len(numbers),
            "Settings": {
                "Population Size": pop_size,
                "Generations": gen_count,
                "Mutation Rate": mut_rate,
                "Tournament Size": tourn_size,
                "Elite Size": elite_size
            },
            "GA Results": ga_results,
            "Status": "Completed"
        }
        
    except Exception as e:
        tracemalloc.stop()
        elapsed = time.time() - start_time
        return {
            "Method": "Genetic Algorithm",
            "Time (s)": round(elapsed, 3),
            "Time Display": format_time(elapsed),
            "Memory (KB)": 0,
            "Matches": 0,
            "Exact Matches": 0,
            "Targets Tested": len(targets),
            "Transactions Used": len(transactions),
            "Settings": {
                "Population Size": pop_size,
                "Generations": gen_count,
                "Mutation Rate": mut_rate,
                "Tournament Size": tourn_size,
                "Elite Size": elite_size
            },
            "Status": f"Failed: {str(e)}"
        }


def run_comprehensive_benchmark(transactions_file, targets_file, output_dir="benchmark_results"):
    """
    Run comprehensive benchmark of all algorithms.
    
    Args:
        transactions_file: Path to transactions file
        targets_file: Path to targets file
        output_dir: Directory to save results
        
    Returns:
        list: All benchmark results
    """
    print("=" * 80)
    print("COMPREHENSIVE SUBSET SUM ALGORITHM BENCHMARK")
    print("=" * 80)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and prepare data
    print("\n📊 Loading and preparing data...")
    try:
        trans_df, target_df = prepare_data(transactions_file, targets_file)
        print(f"✅ Data loaded successfully:")
        print(f"   Transactions: {len(trans_df)} rows")
        print(f"   Targets: {len(target_df)} rows")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return []
    
    # Run benchmarks
    all_results = []
    
    # 1. Brute Force (with safety limits)
    print(f"\n{'='*60}")
    print("1. BRUTE FORCE BENCHMARK")
    print(f"{'='*60}")
    brute_result = run_brute_force_benchmark(trans_df, target_df, max_transactions=15, max_targets=3)
    all_results.append(brute_result)
    
    # 2. Dynamic Programming
    print(f"\n{'='*60}")
    print("2. DYNAMIC PROGRAMMING BENCHMARK")
    print(f"{'='*60}")
    dp_result = run_dynamic_programming_benchmark(trans_df, target_df, precision=100, max_sum_limit=0)
    all_results.append(dp_result)
    
    # 3. Genetic Algorithm
    print(f"\n{'='*60}")
    print("3. GENETIC ALGORITHM BENCHMARK")
    print(f"{'='*60}")
    ga_result = run_genetic_algorithm_benchmark(
        trans_df, target_df, 
        pop_size=100, gen_count=200, mut_rate=0.05, tourn_size=3, elite_size=5
    )
    all_results.append(ga_result)
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("BENCHMARK SUMMARY REPORT")
    print(f"{'='*80}")
    
    summary_data = []
    for result in all_results:
        summary_data.append({
            "Method": result["Method"],
            "Status": result["Status"],
            "Time": result["Time Display"],
            "Memory (KB)": result["Memory (KB)"],
            "Matches": result["Matches"],
            "Targets Tested": result["Targets Tested"],
            "Transactions Used": result["Transactions Used"]
        })
    
    summary_df = pd.DataFrame(summary_data)
    print("\n📊 Performance Summary:")
    print(summary_df.to_string(index=False))
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary
    summary_file = os.path.join(output_dir, f"benchmark_summary_{timestamp}.csv")
    summary_df.to_csv(summary_file, index=False)
    print(f"\n💾 Summary saved to: {summary_file}")
    
    # Save detailed results
    detailed_file = os.path.join(output_dir, f"benchmark_detailed_{timestamp}.csv")
    
    # Flatten detailed results for CSV
    detailed_data = []
    for result in all_results:
        row = {
            "Method": result["Method"],
            "Status": result["Status"],
            "Time (s)": result["Time (s)"],
            "Memory (KB)": result["Memory (KB)"],
            "Matches": result["Matches"],
            "Targets Tested": result["Targets Tested"],
            "Transactions Used": result["Transactions Used"]
        }
        
        # Add settings if available
        if "Settings" in result:
            for key, value in result["Settings"].items():
                row[f"Setting_{key}"] = value
        
        detailed_data.append(row)
    
    detailed_df = pd.DataFrame(detailed_data)
    detailed_df.to_csv(detailed_file, index=False)
    print(f"💾 Detailed results saved to: {detailed_file}")
    
    # Performance analysis
    print(f"\n📈 Performance Analysis:")
    
    # Find best method by different criteria
    successful_results = [r for r in all_results if r["Status"] == "Completed"]
    
    if successful_results:
        # Fastest method
        fastest = min(successful_results, key=lambda x: x["Time (s)"])
        print(f"   🏃 Fastest: {fastest['Method']} ({fastest['Time Display']})")
        
        # Most memory efficient
        most_efficient = min(successful_results, key=lambda x: x["Memory (KB)"])
        print(f"   💾 Most Memory Efficient: {most_efficient['Method']} ({most_efficient['Memory (KB)']} KB)")
        
        # Most matches found
        most_matches = max(successful_results, key=lambda x: x["Matches"])
        print(f"   🎯 Most Matches: {most_matches['Method']} ({most_matches['Matches']} matches)")
        
        # Best match rate
        best_rate = max(successful_results, key=lambda x: x["Matches"] / x["Targets Tested"] if x["Targets Tested"] > 0 else 0)
        rate = (best_rate["Matches"] / best_rate["Targets Tested"]) * 100 if best_rate["Targets Tested"] > 0 else 0
        print(f"   📊 Best Match Rate: {best_rate['Method']} ({rate:.1f}%)")
    
    print(f"\n✅ Benchmark completed successfully!")
    print(f"📁 Results saved in: {output_dir}")
    
    return all_results


if __name__ == "__main__":
    # Test with sample data
    try:
        transactions_file = "data/sample/Customer_Ledger_Entries_FULL.xlsx"
        targets_file = "data/sample/KH_Bank.XLSX"
        
        if os.path.exists(transactions_file) and os.path.exists(targets_file):
            print("🚀 Starting comprehensive benchmark...")
            results = run_comprehensive_benchmark(transactions_file, targets_file)
            print(f"\n🎉 Benchmark completed with {len(results)} methods tested!")
        else:
            print("❌ Data files not found. Please ensure the files exist in the data/sample directory.")
            
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc() 