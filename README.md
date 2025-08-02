# Financial Data Parser

A robust financial data parsing system that can process Excel files, intelligently detect data types, handle various formats, and store data in optimized structures for fast retrieval.

## 🎯 Project Overview

This project implements a comprehensive financial data parsing system with the following capabilities:

- **Excel File Processing**: Read and analyze Excel files with multiple worksheets
- **Intelligent Type Detection**: Automatically classify columns as string, number, or date types
- **Advanced Format Parsing**: Handle complex financial data formats including various currencies and date formats
- **Optimized Data Storage**: Multiple storage strategies with fast query capabilities
- **Data Quality Assurance**: Comprehensive validation and quality analysis

## 📋 Learning Objectives

- Excel file processing with multiple libraries (pandas, openpyxl)
- Data type detection and validation
- Format parsing for financial data
- Data structure optimization for performance
- Error handling and data quality assurance

## 🏗️ Project Structure

```
financial-data-parser/
├── src/
│   ├── core/
│   │   ├── excel_processor.py    # Excel file reading and processing
│   │   ├── type_detector.py      # Data type detection engine
│   │   ├── format_parser.py      # Complex format parsing
│   │   └── data_storage.py       # Optimized data storage system
│   └── utils/
│       ├── helpers.py            # Utility functions
│       └── validators.py         # Data validation functions
├── examples/
│   ├── basic_usage.py           # Phase 1 & 2 demonstration
│   ├── advanced_parsing.py      # Phase 3 demonstration
│   └── performance_demo.py      # Phase 4 demonstration
├── data/
│   └── sample/                  # Sample Excel files
├── tests/                       # Unit tests
└── requirements.txt             # Dependencies
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial-data-parser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python examples/basic_usage.py
```

## 📊 Features

### Phase 1: Basic Excel Processing
- Read Excel files using pandas and openpyxl
- Handle multiple worksheets within each file
- Display basic file information (sheets, dimensions, column names)
- Data preview and inspection capabilities

### Phase 2: Data Type Detection
- **String Columns**: Account names, descriptions, categories, transaction references
- **Number Columns**: Financial amounts, quantities, percentages, account balances
- **Date Columns**: Transaction dates, reporting periods, due dates
- Confidence scoring for type detection

### Phase 3: Format Parsing
- **Amount Formats**:
  - `$1,234.56` (US currency)
  - `€1.234,56` (European format)
  - `₹1,23,456.78` (Indian format)
  - `(1,234.56)` (Negative in parentheses)
  - `1234.56-` (Trailing negative)
  - `1.23K, 2.5M, 1.2B` (Abbreviated amounts)

- **Date Formats**:
  - `MM/DD/YYYY, DD/MM/YYYY`
  - `YYYY-MM-DD, DD-MON-YYYY`
  - `Quarter 1 2024, Q1-24`
  - `Mar 2024, March 2024`
  - Excel serial dates (44927 = Jan 1, 2023)

### Phase 4: Data Storage Optimization
- **Multiple Storage Strategies**:
  - Pandas DataFrame with MultiIndex
  - SQLite in-memory database
  - Dictionary-based indexing
- **Fast Lookup**: Support for range queries and multiple criteria
- **Memory Efficient**: Optimized storage for large datasets
- **Aggregation Capabilities**: Easy data aggregation and analysis

## 💻 Usage Examples

### Basic Usage (Phases 1 & 2)
```python
from src.core.excel_processor import ExcelProcessor
from src.core.type_detector import DataTypeDetector

# Initialize components
excel_processor = ExcelProcessor()
type_detector = DataTypeDetector()

# Load Excel files
file_info = excel_processor.load_files(["data/sample/KH_Bank.XLSX"])

# Analyze data types
df = excel_processor.extract_data("data/sample/KH_Bank.XLSX")
for column in df.columns:
    type_result = type_detector.analyze_column(df[column])
    print(f"{column}: {type_result['type']} ({type_result['confidence']:.2%})")
```

### Advanced Parsing (Phase 3)
```python
from src.core.format_parser import FormatParser

parser = FormatParser()

# Parse amounts
amount_result = parser.parse_amount("$1,234.56")
print(f"Parsed: {amount_result['parsed_value']}, Currency: {amount_result['currency']}")

# Parse dates
date_result = parser.parse_date("Q4 2023")
print(f"Parsed: {date_result['parsed_value']}, Format: {date_result['format']}")
```

### Data Storage and Querying (Phase 4)
```python
from src.core.data_storage import DataStorage

# Initialize storage
storage = DataStorage(storage_type='pandas')

# Store data
dataset_id = storage.store_data(df, {'source': 'sample'})

# Create indexes for fast queries
storage.create_indexes(['date', 'amount'], dataset_id)

# Query data
results = storage.query_by_criteria({
    'amount': {'min': 1000, 'max': 5000},
    'category': 'Revenue'
}, dataset_id)

# Aggregate data
aggregated = storage.aggregate_data(
    group_by=['category'],
    measures=['amount:sum', 'amount:mean']
)
```

## 🧪 Running Examples

### Basic Usage Example
```bash
python examples/basic_usage.py
```

### Advanced Parsing Example
```bash
python examples/advanced_parsing.py
```

### Performance Demo
```bash
python examples/performance_demo.py
```

## 📈 Performance Features

- **Multiple Storage Strategies**: Compare pandas, SQLite, and dictionary storage
- **Indexing Benefits**: See performance improvements with proper indexing
- **Query Optimization**: Fast range queries and complex filtering
- **Memory Management**: Efficient memory usage for large datasets
- **Aggregation Performance**: Optimized aggregation operations

## 🔍 Data Quality Features

- **Automatic Validation**: Validate file formats and data types
- **Quality Scoring**: Overall data quality assessment
- **Issue Detection**: Identify missing data, duplicates, and inconsistencies
- **Recommendations**: Get suggestions for data improvement

## 🛠️ Configuration

The system can be configured through various parameters:

- **Storage Type**: Choose between 'pandas', 'sqlite', or 'dict'
- **Indexing Strategy**: Select columns for indexing
- **Validation Thresholds**: Adjust confidence levels for type detection
- **Performance Monitoring**: Enable detailed performance metrics

## 📝 API Reference

### ExcelProcessor
- `load_files(file_paths)`: Load multiple Excel files
- `get_sheet_info(file_path)`: Get detailed sheet information
- `extract_data(file_path, sheet_name)`: Extract data from specific sheet
- `preview_data(file_path, sheet_name, rows)`: Preview data with specified rows

### DataTypeDetector
- `analyze_column(data)`: Analyze column and determine data type
- `detect_date_format(sample_values)`: Detect date format patterns
- `detect_number_format(sample_values)`: Detect number format patterns
- `classify_string_type(sample_values)`: Classify string data subtypes

### FormatParser
- `parse_amount(value, detected_format)`: Parse amount with various formats
- `parse_date(value, detected_format)`: Parse date with multiple formats
- `normalize_currency(value)`: Normalize currency symbols and separators
- `handle_special_formats(value)`: Handle abbreviated and special formats

### DataStorage
- `store_data(dataframe, metadata)`: Store data with metadata
- `create_indexes(columns, dataset_id)`: Create indexes for fast lookup
- `query_by_criteria(filters, dataset_id)`: Query data with various criteria
- `aggregate_data(group_by, measures, dataset_id)`: Aggregate data with measures

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📊 Sample Data

The project includes sample Excel files in the `data/sample/` directory:
- `KH_Bank.XLSX`: Sample bank transaction data
- `Customer_Ledger_Entries_FULL.xlsx`: Customer ledger entries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions and support:
- Check the examples in the `examples/` directory
- Review the API documentation
- Open an issue for bugs or feature requests

## 🎯 Roadmap

- [ ] Support for additional file formats (CSV, JSON)
- [ ] Real-time data processing capabilities
- [ ] Advanced machine learning for type detection
- [ ] Web interface for data analysis
- [ ] Integration with cloud storage services
- [ ] Advanced visualization capabilities

---

**Built with ❤️ for robust financial data processing**
