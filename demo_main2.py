#!/usr/bin/env python3
"""
Demo script for the Enhanced Fintech Reconciliation System
Shows how to use different reconciliation approaches
"""

from main2 import EnhancedFintechReconciliationSystem
import time

def demo_basic_functionality():
    """Demonstrate basic functionality without running full reconciliation"""
    
    print("Enhanced Fintech Reconciliation System - Demo")
    print("=" * 60)
    
    try:
        # Initialize the system
        print("1. Initializing system...")
        system = EnhancedFintechReconciliationSystem()
        print("   ✓ System initialized successfully")
        
        # Load data
        print("\n2. Loading financial data...")
        system.load_data()
        print("   ✓ Data loaded successfully")
        
        # Show data overview
        print(f"\n3. Data Overview:")
        print(f"   Customer Ledger: {len(system.customer_ledger)} records")
        print(f"   Bank Statement: {len(system.bank_statement)} records")
        
        # Show identified columns
        print(f"\n4. Identified Key Columns:")
        print(f"   Ledger Amount: {system.primary_amount_col_ledger}")
        print(f"   Ledger Description: {system.primary_desc_col_ledger}")
        print(f"   Bank Amount: {system.primary_amount_col_bank}")
        print(f"   Bank Description: {system.primary_desc_col_bank}")
        
        return system
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def demo_exact_matching(system):
    """Demonstrate exact amount matching"""
    
    print("\n" + "=" * 40)
    print("DEMO: Exact Amount Matching")
    print("=" * 40)
    
    try:
        start_time = time.time()
        exact_matches = system.exact_amount_matching(tolerance=0.01)
        end_time = time.time()
        
        print(f"✓ Exact matching completed in {end_time - start_time:.2f} seconds")
        print(f"  Found {len(exact_matches)} exact matches")
        
        if len(exact_matches) > 0:
            print("\n  Sample matches:")
            print(exact_matches.head(3).to_string())
        
        return exact_matches
        
    except Exception as e:
        print(f"✗ Error in exact matching: {e}")
        return None

def demo_subset_sum_matching(system):
    """Demonstrate subset sum matching with efficient algorithm"""
    
    print("\n" + "=" * 40)
    print("DEMO: Subset Sum Matching (Efficient Algorithm)")
    print("=" * 40)
    
    try:
        start_time = time.time()
        subset_matches = system.advanced_subset_sum_matching(max_combination_size=3, tolerance=0.01)
        end_time = time.time()
        
        print(f"✓ Subset sum matching completed in {end_time - start_time:.2f} seconds")
        print(f"  Found {len(subset_matches)} subset combinations")
        
        if len(subset_matches) > 0:
            print("\n  Sample subset matches:")
            print(subset_matches.head(3).to_string())
        
        return subset_matches
        
    except Exception as e:
        print(f"✗ Error in subset sum matching: {e}")
        return None

def demo_fuzzy_matching(system):
    """Demonstrate fuzzy matching"""
    
    print("\n" + "=" * 40)
    print("DEMO: Fuzzy Matching")
    print("=" * 40)
    
    try:
        start_time = time.time()
        fuzzy_matches = system.fuzzy_matching(amount_tolerance=0.05, text_similarity_threshold=0.3)
        end_time = time.time()
        
        print(f"✓ Fuzzy matching completed in {end_time - start_time:.2f} seconds")
        print(f"  Found {len(fuzzy_matches)} fuzzy matches")
        
        if len(fuzzy_matches) > 0:
            print("\n  Sample fuzzy matches:")
            print(fuzzy_matches.head(3).to_string())
        
        return fuzzy_matches
        
    except Exception as e:
        print(f"✗ Error in fuzzy matching: {e}")
        return None



def main():
    """Run the complete demo"""
    
    print("Starting Enhanced Fintech Reconciliation System Demo...")
    print("This demo will show all three reconciliation approaches:")
    print("1. Exact Amount Matching")
    print("2. Subset Sum Matching (Efficient Algorithm)")
    print("3. Fuzzy Matching")
    print("\nNote: This demo processes limited data for performance.")
    
    # Initialize and load data
    system = demo_basic_functionality()
    if system is None:
        print("\n❌ Demo failed during initialization. Please check your data files.")
        return
    
    # Run individual demos
    results = {}
    
    # Demo 1: Exact matching
    results['exact'] = demo_exact_matching(system)
    
    # Demo 2: Subset sum matching
    results['subset'] = demo_subset_sum_matching(system)
    
    # Demo 3: Fuzzy matching
    results['fuzzy'] = demo_fuzzy_matching(system)
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    
    total_matches = sum(len(df) if df is not None else 0 for df in results.values())
    successful_demos = sum(1 for df in results.values() if df is not None)
    
    print(f"Successful demos: {successful_demos}/3")
    print(f"Total matches found: {total_matches}")
    
    for demo_name, result in results.items():
        if result is not None:
            print(f"  {demo_name.replace('_', ' ').title()}: {len(result)} matches")
        else:
            print(f"  {demo_name.replace('_', ' ').title()}: Failed")
    
    print("\n🎉 Demo completed successfully!")
    print("\nTo run the full reconciliation system, use:")
    print("  python main2.py")

if __name__ == "__main__":
    main() 