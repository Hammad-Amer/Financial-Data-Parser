#!/usr/bin/env python3
"""
Test script to verify subset sum improvements
"""

from main2 import EnhancedFintechReconciliationSystem
import time

def test_subset_sum_improvements():
    """Test the improved subset sum matching"""
    
    print("Testing Subset Sum Improvements...")
    print("=" * 50)
    
    try:
        # Initialize system
        system = EnhancedFintechReconciliationSystem()
        system.load_data()
        
        print(f"Dataset loaded:")
        print(f"  Customer Ledger: {len(system.customer_ledger)} records")
        print(f"  Bank Statement: {len(system.bank_statement)} records")
        
        # Test with a small subset first
        print(f"\nTesting with first 5 bank entries...")
        start_time = time.time()
        
        # Test the improved dynamic programming method
        test_amounts = [(i, amt) for i, amt in enumerate(system.customer_ledger[system.primary_amount_col_ledger].values[:100])]
        target_amount = system.bank_statement[system.primary_amount_col_bank].values[0]
        
        print(f"Target amount: {target_amount}")
        print(f"Testing with {len(test_amounts)} ledger amounts...")
        
        combinations = system.dynamic_programming_subset_sum(
            target_amount, test_amounts, tolerance=0.01, max_combination_size=3
        )
        
        end_time = time.time()
        print(f"Dynamic programming completed in {end_time - start_time:.2f} seconds")
        print(f"Found {len(combinations)} combinations")
        
        if len(combinations) > 0:
            print("Sample combinations:")
            for i, combo in enumerate(combinations[:3]):
                combo_amounts = [test_amounts[idx][1] for idx in combo]
                combo_sum = sum(combo_amounts)
                print(f"  {i+1}: {combo_amounts} = {combo_sum} (diff: {abs(combo_sum - target_amount):.2f})")
        
        # Test the simple method
        print(f"\nTesting simple subset sum method...")
        start_time = time.time()
        
        simple_matches = system.simple_subset_sum_matching(max_entries=5, max_combination_size=3)
        
        end_time = time.time()
        print(f"Simple method completed in {end_time - start_time:.2f} seconds")
        print(f"Found {len(simple_matches)} matches")
        
        if len(simple_matches) > 0:
            print("Sample matches:")
            print(simple_matches.head(3).to_string())
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_subset_sum_improvements() 