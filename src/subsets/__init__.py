"""
Subset Sum Algorithms Package

This package contains implementations of various algorithms for solving the subset sum problem:
- Brute Force approach
- Dynamic Programming approach  
- Genetic Algorithm approach
- Feature Engineering utilities
"""

# Note: These imports will work when the package is properly installed
# or when the src directory is in the Python path
try:
    from src.subsets.brute_force import prepare_data, brute_force_subset
    from src.subsets.genetic_algorithm import SubsetSumGA
    from src.subsets.dynamic_programming import subset_sum_exists, subset_sum_exists_optimized
    from src.subsets.feature_engineering import generate_candidates, feature_engineering
except ImportError:
    # Fallback for when running from within the package
    from .brute_force import prepare_data, brute_force_subset
    from .genetic_algorithm import SubsetSumGA
    from .dynamic_programming import subset_sum_exists, subset_sum_exists_optimized
    from .feature_engineering import generate_candidates, feature_engineering

__all__ = [
    'prepare_data',
    'brute_force_subset', 
    'SubsetSumGA',
    'subset_sum_exists',
    'subset_sum_exists_optimized',
    'generate_candidates',
    'feature_engineering'
] 