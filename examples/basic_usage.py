#!/usr/bin/env python3
"""
Basic Usage Example for Financial Data Parser

This example demonstrates:
- Phase 1: Basic Excel file processing
- Phase 2: Data type detection
- Basic data preview and analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.excel_processor import ExcelProcessor
from src.core.type_detector import DataTypeDetector
from src.utils.helpers import get_file_info, create_summary_report
from src.utils.validators import validate_file_format


def main():
    """Main function demonstrating basic usage."""
    print("=== Financial Data Parser - Basic Usage Example ===\n")
    
    # Initialize components
    excel_processor = ExcelProcessor()
    type_detector = DataTypeDetector()
    
    # Define file paths
    sample_files = [
        "data/sample/KH_Bank.XLSX",
        "data/sample/Customer_Ledger_Entries_FULL.xlsx"
    ]
    
    print("1. Loading Excel Files...")
    print("-" * 40)
    
    # Validate and load files
    for file_path in sample_files:
        print(f"\nProcessing: {file_path}")
        
        # Validate file format
        validation = validate_file_format(file_path)
        if not validation['is_valid']:
            print(f"❌ File validation failed: {validation['error']}")
            continue
        
        print(f"✅ File validated: {validation['file_type']} format")
        print(f"   Sheets: {validation['sheet_count']}")
        print(f"   Size: {validation['file_info']['size_mb']} MB")
    
    # Load files into processor
    try:
        file_info = excel_processor.load_files(sample_files)
        print(f"\n✅ Successfully loaded {len(file_info)} files")
    except Exception as e:
        print(f"❌ Error loading files: {str(e)}")
        return
    
    print("\n2. Analyzing File Structure...")
    print("-" * 40)
    
    # Analyze each file
    for file_path in sample_files:
        print(f"\n📊 File: {os.path.basename(file_path)}")
        
        # Get sheet information
        sheet_info = excel_processor.get_sheet_info(file_path)
        
        for sheet_name, info in sheet_info.items():
            if 'error' in info:
                print(f"   ❌ Sheet '{sheet_name}': {info['error']}")
                continue
            
            print(f"   📋 Sheet: {sheet_name}")
            print(f"      Dimensions: {info['dimensions']}")
            print(f"      Columns: {info['column_count']}")
            print(f"      Sample rows: {info['sample_rows']}")
            
            # Preview data
            try:
                preview_df = excel_processor.preview_data(file_path, sheet_name, rows=3)
                print(f"      Sample data:")
                for i, row in preview_df.iterrows():
                    print(f"        Row {i+1}: {list(row.values)[:3]}...")
            except Exception as e:
                print(f"      ❌ Error previewing data: {str(e)}")
    
    print("\n3. Data Type Detection...")
    print("-" * 40)
    
    # Perform type detection on each file
    for file_path in sample_files:
        print(f"\n🔍 Analyzing data types for: {os.path.basename(file_path)}")
        
        # Get all sheets data
        all_sheets_data = excel_processor.get_all_sheets_data(file_path)
        
        for sheet_name, df in all_sheets_data.items():
            print(f"\n   📊 Sheet: {sheet_name}")
            print(f"      Shape: {df.shape}")
            
            # Analyze each column
            column_analysis = {}
            for column in df.columns:
                print(f"      🔍 Column: {column}")
                
                # Detect type
                type_result = type_detector.analyze_column(df[column])
                
                print(f"         Type: {type_result['type']}")
                print(f"         Confidence: {type_result['confidence']:.2%}")
                
                # Show format information
                if 'format_info' in type_result:
                    format_info = type_result['format_info']
                    if type_result['type'] == 'number':
                        if 'currency_symbols' in format_info and format_info['currency_symbols']:
                            print(f"         Currency: {format_info['currency_symbols']}")
                        if 'abbreviated_formats' in format_info and format_info['abbreviated_formats']:
                            print(f"         Abbreviated formats detected")
                    elif type_result['type'] == 'date':
                        if 'detected_patterns' in format_info and format_info['detected_patterns']:
                            print(f"         Date patterns: {format_info['detected_patterns']}")
                        if 'excel_serial_dates' in format_info and format_info['excel_serial_dates']:
                            print(f"         Excel serial dates detected")
                
                column_analysis[column] = type_result
            
            # Create summary report
            summary = create_summary_report(df, f"Analysis of {sheet_name}")
            print(f"\n      📈 Summary:")
            print(f"         Rows: {summary['basic_info']['rows']}")
            print(f"         Columns: {summary['basic_info']['columns']}")
            print(f"         Memory usage: {summary['basic_info']['memory_usage_mb']} MB")
            print(f"         Null values: {summary['basic_info']['null_values']}")
    
    print("\n4. Data Quality Assessment...")
    print("-" * 40)
    
    # Assess data quality
    for file_path in sample_files:
        print(f"\n🔍 Quality assessment for: {os.path.basename(file_path)}")
        
        all_sheets_data = excel_processor.get_all_sheets_data(file_path)
        
        for sheet_name, df in all_sheets_data.items():
            print(f"\n   📊 Sheet: {sheet_name}")
            
            # Basic quality metrics
            null_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            duplicate_rows = df.duplicated().sum()
            
            print(f"      Null percentage: {null_percentage:.2f}%")
            print(f"      Duplicate rows: {duplicate_rows}")
            print(f"      Unique values per column:")
            
            for column in df.columns:
                unique_count = df[column].nunique()
                total_count = len(df)
                unique_percentage = (unique_count / total_count) * 100
                print(f"         {column}: {unique_count}/{total_count} ({unique_percentage:.1f}%)")
    
    print("\n✅ Basic usage example completed!")
    print("\nNext steps:")
    print("- Try advanced_parsing.py for format parsing examples")
    print("- Try performance_demo.py for performance analysis")
    print("- Check the documentation for more features")


if __name__ == "__main__":
    main()
