#!/usr/bin/env python3
"""
Test script to verify subset sum module integration
"""

import sys
import os

# Add src directory to path
sys.path.append('src')

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from subsets.brute_force import prepare_data, brute_force_subset
        print("✅ Brute force module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import brute force module: {e}")
        return False
    
    try:
        from subsets.genetic_algorithm import SubsetSumGA
        print("✅ Genetic algorithm module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import genetic algorithm module: {e}")
        return False
    
    try:
        from subsets.dynamic_programming import subset_sum_exists, subset_sum_exists_optimized
        print("✅ Dynamic programming module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import dynamic programming module: {e}")
        return False
    
    try:
        from subsets.feature_engineering import generate_candidates, feature_engineering
        print("✅ Feature engineering module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import feature engineering module: {e}")
        return False
    
    try:
        from subsets.run_benchmarking import run_comprehensive_benchmark
        print("✅ Benchmarking module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import benchmarking module: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic functionality without requiring data files"""
    print("\nTesting basic functionality...")
    
    try:
        # Test genetic algorithm initialization
        from subsets.genetic_algorithm import SubsetSumGA
        
        # Simple test with small numbers
        test_numbers = [1, 2, 3, 4, 5]
        test_targets = [6, 10]
        
        ga = SubsetSumGA(test_numbers, test_targets, pop_size=10, gen_count=10)
        print("✅ Genetic algorithm initialized successfully")
        
        # Test feature engineering with dummy data
        import pandas as pd
        
        dummy_trans = pd.DataFrame({
            'Transaction ID': ['TX001', 'TX002'],
            'amount': [100, 200]
        })
        
        dummy_targets = pd.DataFrame({
            'Target ID': ['TG001'],
            'amount': [300]
        })
        
        from subsets.feature_engineering import generate_candidates
        candidates = generate_candidates(dummy_trans, dummy_targets)
        print(f"✅ Feature engineering generated {len(candidates)} candidates")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("SUBSET SUM MODULE INTEGRATION TEST")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check module structure.")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed.")
        return False
    
    print("\n✅ All tests passed successfully!")
    print("\nThe subset sum modules are properly integrated and ready to use.")
    print("\nNext steps:")
    print("1. Run 'python subset_sum_demo.py' for a comprehensive demonstration")
    print("2. Use the Streamlit dashboard '💰 Subset Sum' tab")
    print("3. Import modules in your own scripts")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 