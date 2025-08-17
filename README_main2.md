# Enhanced Fintech Reconciliation System

## Overview

This is a comprehensive financial reconciliation system that implements multiple approaches to match financial transactions between Customer Ledger Entries and Bank Statements. The system addresses the requirements from the Excel Sheet Reconciliation Assignment, implementing both brute force and machine learning approaches.

## Features

### 1. **Exact Amount Matching**
- Direct matching between individual transactions
- Configurable tolerance for amount differences
- High confidence scoring

### 2. **Subset Sum Matching (Dynamic Programming)**
- **Task 3.2: Dynamic Programming Enhancement**
- Finds combinations of ledger transactions that sum to bank statement amounts
- Optimized using dynamic programming for better performance
- Configurable maximum combination size and tolerance

### 3. **Fuzzy Matching with Similarity Scores**
- **Task 4.2: Fuzzy Matching with Similarity Scores**
- Combines amount proximity and text similarity
- Multiple similarity algorithms (Jaccard, character-based, substring)
- Configurable thresholds for amount and text similarity



## Implementation Details

### Core Components

- **`EnhancedFintechReconciliationSystem`**: Main class containing all reconciliation logic
- **Column Identification**: Automatically identifies amount and description columns
- **Data Cleaning**: Handles missing values, currency symbols, and data standardization
- **Performance Optimization**: Limits processing to prevent excessive runtime

### Key Methods

#### Data Processing
- `load_data()`: Loads Excel files and identifies key columns
- `identify_key_columns()`: Automatically finds relevant columns for matching
- `clean_and_prepare_data()`: Standardizes and cleans financial data

#### Matching Algorithms
- `exact_amount_matching()`: Direct amount matching with tolerance
- `dynamic_programming_subset_sum()`: Optimized subset sum algorithm
- `advanced_subset_sum_matching()`: High-level subset sum matching
- `fuzzy_matching()`: Enhanced fuzzy matching with multiple similarity metrics

#### Analysis and Reporting
- `run_comprehensive_reconciliation()`: Runs all matching methods
- `generate_summary_report()`: Comprehensive results summary
- `save_results_to_files()`: Exports results to CSV files

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Required Packages**:
   - pandas >= 1.5.0
   - openpyxl >= 3.0.0
   - numpy >= 1.21.0
   - scikit-learn >= 1.0.0
   - matplotlib >= 3.5.0
   - seaborn >= 0.11.0

## Usage

### Quick Start

```python
from main2 import EnhancedFintechReconciliationSystem

# Initialize the system
system = EnhancedFintechReconciliationSystem()

# Run comprehensive reconciliation
results = system.run_comprehensive_reconciliation()
```

### Individual Methods

```python
# Exact matching
exact_matches = system.exact_amount_matching(tolerance=0.01)

# Subset sum matching
subset_matches = system.advanced_subset_sum_matching(max_combination_size=4)

# Fuzzy matching
fuzzy_matches = system.fuzzy_matching(amount_tolerance=0.05, text_similarity_threshold=0.3)

# ML-enhanced matching
ml_matches = system.ml_enhanced_matching(confidence_threshold=0.6)
```

### Demo Script

Run the interactive demo to see all methods in action:
```bash
python demo_main2.py
```

### Full System

Run the complete reconciliation system:
```bash
python main2.py
```

## Data Requirements

### Input Files
- **Customer Ledger Entries**: Excel file with transaction amounts and descriptions
- **Bank Statement**: Excel file with target amounts and reference information

### Expected Columns
The system automatically identifies columns, but typically expects:
- **Amount columns**: Column A (Customer Ledger), Column C (Bank Statement)
- **Description columns**: Column B (Customer Ledger), Column D (Bank Statement)

## Performance Considerations

- **Processing Limits**: System limits processing to prevent excessive runtime
- **Dynamic Programming**: Optimized subset sum algorithm for better performance
- **Batch Processing**: Processes data in manageable chunks
- **Memory Management**: Efficient data structures and cleanup

## Output

### Results
- **Exact Matches**: Direct amount matches with confidence scores
- **Subset Combinations**: Multi-transaction combinations that sum to targets
- **Fuzzy Matches**: Approximate matches based on amount and text similarity

### Files Generated
- CSV files for each matching method with timestamps
- Comprehensive summary report in console output
- Performance metrics and coverage analysis

## Configuration

### Adjustable Parameters
- **Tolerance**: Amount matching tolerance (default: 0.01)
- **Combination Size**: Maximum subset combination size (default: 4)
- **Similarity Thresholds**: Text and amount similarity thresholds

### Performance Tuning
- **Max Bank Entries**: Limit bank statement processing (default: 200-300)
- **Max Ledger Entries**: Limit ledger processing (default: 300-500)
- **Training Data Size**: ML training examples (default: 100 positive, 200 negative)

## Testing

Run the test suite to verify implementation:
```bash
python test_main2.py
```

## Architecture

### Class Structure
```
EnhancedFintechReconciliationSystem
├── Data Management
│   ├── load_data()
│   ├── identify_key_columns()
│   └── clean_and_prepare_data()
├── Matching Algorithms
│   ├── exact_amount_matching()
│   ├── advanced_subset_sum_matching()
│   ├── fuzzy_matching()
│   └── ml_enhanced_matching()
├── Machine Learning
│   ├── create_ml_features()
│   ├── prepare_ml_training_data()
│   └── train_ml_matching_model()
└── Analysis & Reporting
    ├── run_comprehensive_reconciliation()
    ├── generate_summary_report()
    └── save_results_to_files()
```

## Future Enhancements

- **Genetic Algorithm**: Task 4.1 implementation for subset selection
- **Performance Benchmarking**: Task 5.1 comprehensive performance comparison
- **Advanced Visualizations**: Task 5.2 enhanced reporting and charts
- **Real-time Processing**: Stream processing for live data
- **API Integration**: REST API for external system integration

## Troubleshooting

### Common Issues
1. **File Not Found**: Ensure Excel files are in `data/sample/` directory
2. **Column Identification**: Check if expected columns exist in your data
3. **Memory Issues**: Reduce processing limits for large datasets
4. **ML Training**: Ensure sufficient positive examples for model training

### Performance Tips
- Use smaller tolerance values for faster exact matching
- Limit combination sizes for subset sum matching
- Adjust similarity thresholds based on data quality
- Monitor memory usage with large datasets

## License

This implementation is part of the Financial Data Parser project and follows the project's licensing terms.

## Support

For issues or questions about this implementation, refer to the project documentation or create an issue in the project repository. 