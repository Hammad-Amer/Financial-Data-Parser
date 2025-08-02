import os
import sys
import pandas as pd
from src.core.excel_processor import ExcelProcessor
from src.core.type_detector import DataTypeDetector
from src.core.format_parser import FormatParser
from src.core.data_storage import DataStorage

# Sample test cases and documentation (from your images)
SAMPLE_TEST_CASES = '''\
Sample Test Cases
----------------
# Test amount parsing
test_amounts = [
    "$1,234.56",
    "(2,500.00)",
    "€1.234,56",
    "1.5M",
    "₹1,23,456"
]

# Test date parsing
test_dates = [
    "12/31/2023",
    "2023-12-31",
    "Q4 2023",
    "Dec-23",
    "44927"  # Excel serial
]
'''

RESOURCES = '''\
Resources and References
-----------------------
- Pandas Documentation: Data manipulation basics
- OpenPyXL Guide: Advanced Excel operations
- Regular Expressions: Pattern matching for formats
- SQLite Tutorial: Database operations
- Performance Profiling: cProfile and memory_profiler
'''

GETTING_STARTED = '''\
Getting Started
---------------
1. Use project repository
2. Install required dependencies
3. Sample financial data files are inside data/sample folder
4. Start with Phase 1 implementation
'''

DELIVERABLES = '''\
Deliverables
------------
Foundation
- Excel file reading functionality
- Basic data preview and inspection
- Initial data type detection

Advanced Parsing
- Robust amount parsing (multiple formats)
- Date parsing with format detection
- Error handling and validation

Storage Optimization
- Implement multiple storage strategies
- Performance benchmarking
- Query optimization

Integration & Testing
- Complete integration testing
'''

PROJECT_OVERVIEW = '''\
Financial Data Parser
--------------------
Build a robust financial data parsing system that can process Excel files, intelligently detect data types, handle various formats, and store data in optimized structures for fast retrieval.
'''

# Main menu
MENU = '''\n\n=== Financial Data Parser Main Menu ===
1. Load Excel files
2. Preview file/sheet info
3. Preview sample data
4. Detect column data types
5. Parse sample amounts/dates
6. Store and index data
7. Query data
8. Aggregate data
9. Show sample test cases
10. Show documentation/resources
0. Exit\n'''

def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def main():
    excel_processor = ExcelProcessor()
    type_detector = DataTypeDetector()
    format_parser = FormatParser()
    data_storage = DataStorage()
    loaded_files = []
    dataset_ids = []

    while True:
        print(MENU)
        choice = input("Select an option: ").strip()
        if choice == '1':
            print_header("Load Excel Files")
            file_paths = input("Enter comma-separated Excel file paths (or press Enter for sample files): ").strip()
            if not file_paths:
                file_paths = ["data/sample/KH_Bank.XLSX", "data/sample/Customer_Ledger_Entries_FULL.xlsx"]
            else:
                file_paths = [f.strip() for f in file_paths.split(",")]
            try:
                file_info = excel_processor.load_files(file_paths)
                loaded_files = list(file_info.keys())
                print(f"Loaded files: {loaded_files}")
            except Exception as e:
                print(f"Error loading files: {e}")
        elif choice == '2':
            print_header("Preview File/Sheet Info")
            if not loaded_files:
                print("No files loaded. Please load files first.")
                continue
            for file_path in loaded_files:
                print(f"\nFile: {file_path}")
                try:
                    sheet_info = excel_processor.get_sheet_info(file_path)
                    for sheet, info in sheet_info.items():
                        print(f"  Sheet: {sheet}")
                        for k, v in info.items():
                            print(f"    {k}: {v}")
                except Exception as e:
                    print(f"  Error: {e}")
        elif choice == '3':
            print_header("Preview Sample Data")
            if not loaded_files:
                print("No files loaded. Please load files first.")
                continue
            for file_path in loaded_files:
                sheet_info = excel_processor.get_sheet_info(file_path)
                for sheet in sheet_info:
                    print(f"\nFile: {file_path}, Sheet: {sheet}")
                    try:
                        df = excel_processor.preview_data(file_path, sheet, rows=5)
                        print(df.head())
                    except Exception as e:
                        print(f"  Error: {e}")
        elif choice == '4':
            print_header("Detect Column Data Types")
            if not loaded_files:
                print("No files loaded. Please load files first.")
                continue
            for file_path in loaded_files:
                all_sheets = excel_processor.get_all_sheets_data(file_path)
                for sheet, df in all_sheets.items():
                    print(f"\nFile: {file_path}, Sheet: {sheet}")
                    for col in df.columns:
                        result = type_detector.analyze_column(df[col])
                        print(f"  Column: {col} => Type: {result['type']}, Confidence: {result['confidence']:.2f}")
        elif choice == '5':
            print_header("Parse Sample Amounts/Dates")
            print("Sample Amounts:")
            test_amounts = ["$1,234.56", "(2,500.00)", "€1.234,56", "1.5M", "₹1,23,456"]
            for amt in test_amounts:
                parsed = format_parser.parse_amount(amt)
                print(f"  {amt} => {parsed}")
            print("\nSample Dates:")
            test_dates = ["12/31/2023", "2023-12-31", "Q4 2023", "Dec-23", "44927"]
            for dt in test_dates:
                parsed = format_parser.parse_date(dt)
                print(f"  {dt} => {parsed}")
        elif choice == '6':
            print_header("Store and Index Data")
            if not loaded_files:
                print("No files loaded. Please load files first.")
                continue
            for file_path in loaded_files:
                all_sheets = excel_processor.get_all_sheets_data(file_path)
                for sheet, df in all_sheets.items():
                    # Use type detection for metadata
                    metadata = {col: type_detector.analyze_column(df[col]) for col in df.columns}
                    ds_id = data_storage.store_data(df, metadata)
                    dataset_ids.append(ds_id)
                    print(f"Stored dataset: {ds_id} (File: {file_path}, Sheet: {sheet})")
                    # Create indexes for all columns
                    idx_info = data_storage.create_indexes(list(df.columns), ds_id)
                    print(f"  Indexes created: {list(idx_info[ds_id].keys())}")
        elif choice == '7':
            print_header("Query Data")
            if not dataset_ids:
                print("No datasets stored. Please store data first.")
                continue
            print(f"Available datasets: {dataset_ids}")
            ds_id = input("Enter dataset id to query (or leave blank for all): ").strip() or None
            col = input("Enter column to filter: ").strip()
            val = input("Enter value to match: ").strip()
            filters = {col: val}
            try:
                result = data_storage.query_by_criteria(filters, ds_id)
                print(result.head())
            except Exception as e:
                print(f"Error querying data: {e}")
        elif choice == '8':
            print_header("Aggregate Data")
            if not dataset_ids:
                print("No datasets stored. Please store data first.")
                continue
            print(f"Available datasets: {dataset_ids}")
            ds_id = input("Enter dataset id to aggregate (or leave blank for all): ").strip() or None
            group_by = input("Enter group by columns (comma-separated): ").strip().split(',')
            measures = input("Enter measure columns (comma-separated): ").strip().split(',')
            try:
                result = data_storage.aggregate_data([g.strip() for g in group_by if g.strip()], [m.strip() for m in measures if m.strip()], ds_id)
                print(result)
            except Exception as e:
                print(f"Error aggregating data: {e}")
        elif choice == '9':
            print_header("Sample Test Cases")
            print(SAMPLE_TEST_CASES)
        elif choice == '10':
            print_header("Documentation & Resources")
            print(PROJECT_OVERVIEW)
            print(RESOURCES)
        elif choice == '0':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main() 