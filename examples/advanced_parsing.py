#!/usr/bin/env python3
"""
Advanced Parsing Example for Financial Data Parser

This example demonstrates:
- Phase 3: Complex format parsing
- Amount parsing with various formats
- Date parsing with multiple formats
- Error handling and validation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.format_parser import FormatParser
from src.core.type_detector import DataTypeDetector
from src.utils.validators import validate_amount_format, validate_date_format


def test_amount_parsing():
    """Test amount parsing with various formats."""
    print("=== Amount Format Parsing Tests ===\n")
    
    parser = FormatParser()
    
    # Test cases for amount parsing
    test_amounts = [
        "$1,234.56",           # US currency
        "€1.234,56",           # European format
        "₹1,23,456.78",        # Indian format
        "(1,234.56)",          # Negative in parentheses
        "1234.56-",            # Trailing negative
        "1.23K",               # Abbreviated (K)
        "2.5M",                # Abbreviated (M)
        "1.2B",                # Abbreviated (B)
        "1000",                # Plain number
        "-500",                # Negative number
        "$0.00",               # Zero amount
        "1,000,000",           # Large number with commas
        "€1,234.56",           # Euro with standard format
        "Invalid",             # Invalid format
        "",                    # Empty string
        None                   # None value
    ]
    
    print("Testing various amount formats:")
    print("-" * 60)
    
    for amount in test_amounts:
        print(f"\nInput: {amount}")
        
        # Parse amount
        result = parser.parse_amount(amount)
        
        if result.get('error'):
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Parsed: {result['parsed_value']}")
            print(f"     Currency: {result.get('currency', 'None')}")
            print(f"     Negative: {result['is_negative']}")
            
            if 'abbreviation' in result:
                print(f"     Abbreviation: {result['abbreviation']}")
                print(f"     Multiplier: {result['multiplier']}")
                print(f"     Base value: {result['base_value']}")
            
            if 'format' in result:
                print(f"     Format: {result['format']}")
    
    print("\n" + "=" * 60)


def test_date_parsing():
    """Test date parsing with various formats."""
    print("\n=== Date Format Parsing Tests ===\n")
    
    parser = FormatParser()
    
    # Test cases for date parsing
    test_dates = [
        "12/31/2023",          # MM/DD/YYYY
        "31/12/2023",          # DD/MM/YYYY
        "2023-12-31",          # YYYY-MM-DD
        "31-Dec-2023",         # DD-MON-YYYY
        "Q4 2023",             # Quarter format
        "Q1-24",               # Quarter short format
        "Dec 2023",            # Month-Year
        "March 2024",          # Full month name
        "44927",               # Excel serial date
        "2023-12-31 14:30:00", # DateTime
        "Invalid Date",        # Invalid format
        "",                    # Empty string
        None                   # None value
    ]
    
    print("Testing various date formats:")
    print("-" * 60)
    
    for date_value in test_dates:
        print(f"\nInput: {date_value}")
        
        # Parse date
        result = parser.parse_date(date_value)
        
        if result.get('error'):
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Parsed: {result['parsed_value']}")
            print(f"     Format: {result['format']}")
            
            if 'year' in result:
                print(f"     Year: {result['year']}")
                print(f"     Month: {result['month']}")
                print(f"     Day: {result['day']}")
            
            if 'quarter' in result:
                print(f"     Quarter: {result['quarter']}")
            
            if 'serial_date' in result:
                print(f"     Excel serial: {result['serial_date']}")
    
    print("\n" + "=" * 60)


def test_validation_functions():
    """Test validation functions."""
    print("\n=== Validation Function Tests ===\n")
    
    # Test amount validation
    print("Amount Format Validation:")
    print("-" * 40)
    
    test_amounts = [
        "$1,234.56",
        "(2,500.00)",
        "€1.234,56",
        "1.5M",
        "₹1,23,456",
        "Invalid"
    ]
    
    for amount in test_amounts:
        validation = validate_amount_format(amount)
        status = "✅" if validation['is_valid'] else "❌"
        print(f"{status} {amount}: {validation.get('pattern', validation.get('error'))}")
    
    # Test date validation
    print("\nDate Format Validation:")
    print("-" * 40)
    
    test_dates = [
        "12/31/2023",
        "2023-12-31",
        "Q4 2023",
        "Dec-23",
        "44927",
        "Invalid"
    ]
    
    for date_value in test_dates:
        validation = validate_date_format(date_value)
        status = "✅" if validation['is_valid'] else "❌"
        print(f"{status} {date_value}: {validation.get('pattern', validation.get('error'))}")
    
    print("\n" + "=" * 60)


def test_type_detection_with_parsing():
    """Test type detection combined with format parsing."""
    print("\n=== Type Detection with Format Parsing ===\n")
    
    import pandas as pd
    
    # Create sample data with various formats
    sample_data = {
        'amounts': [
            "$1,234.56", "€1.234,56", "(500.00)", "2.5M", "1000", "Invalid"
        ],
        'dates': [
            "12/31/2023", "Q4 2023", "Dec 2023", "44927", "Invalid", "2023-12-31"
        ],
        'strings': [
            "Account 123", "Transaction Ref", "Company Inc", "Description", "Notes", "Final"
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Initialize components
    type_detector = DataTypeDetector()
    format_parser = FormatParser()
    
    print("Sample Data:")
    print(df.to_string())
    print("\n" + "-" * 60)
    
    # Analyze each column
    for column in df.columns:
        print(f"\n🔍 Analyzing column: {column}")
        
        # Type detection
        type_result = type_detector.analyze_column(df[column])
        print(f"   Detected type: {type_result['type']}")
        print(f"   Confidence: {type_result['confidence']:.2%}")
        
        # Parse values based on detected type
        print(f"   Parsing results:")
        for value in df[column]:
            if type_result['type'] == 'number':
                parsed = format_parser.parse_amount(value)
                if parsed.get('error'):
                    print(f"     ❌ {value}: {parsed['error']}")
                else:
                    print(f"     ✅ {value} → {parsed['parsed_value']}")
            
            elif type_result['type'] == 'date':
                parsed = format_parser.parse_date(value)
                if parsed.get('error'):
                    print(f"     ❌ {value}: {parsed['error']}")
                else:
                    print(f"     ✅ {value} → {parsed['parsed_value']}")
            
            else:
                print(f"     📝 {value} (string)")
    
    print("\n" + "=" * 60)


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n=== Error Handling Tests ===\n")
    
    parser = FormatParser()
    
    # Test edge cases
    edge_cases = [
        None,                   # None value
        "",                     # Empty string
        "   ",                  # Whitespace only
        "0",                    # Zero
        "0.0",                  # Zero decimal
        "-0",                   # Negative zero
        "999999999999999",      # Very large number
        "0.0000000000001",      # Very small number
        "2023-13-45",           # Invalid date
        "25:70:90",             # Invalid time
        "Q5 2023",              # Invalid quarter
        "13th Month 2023",      # Invalid month
    ]
    
    print("Testing edge cases and error handling:")
    print("-" * 50)
    
    for case in edge_cases:
        print(f"\nInput: {case}")
        
        # Test amount parsing
        amount_result = parser.parse_amount(case)
        if amount_result.get('error'):
            print(f"  Amount: ❌ {amount_result['error']}")
        else:
            print(f"  Amount: ✅ {amount_result['parsed_value']}")
        
        # Test date parsing
        date_result = parser.parse_date(case)
        if date_result.get('error'):
            print(f"  Date: ❌ {date_result['error']}")
        else:
            print(f"  Date: ✅ {date_result['parsed_value']}")
    
    print("\n" + "=" * 60)


def main():
    """Main function demonstrating advanced parsing."""
    print("=== Financial Data Parser - Advanced Parsing Example ===\n")
    
    # Run all tests
    test_amount_parsing()
    test_date_parsing()
    test_validation_functions()
    test_type_detection_with_parsing()
    test_error_handling()
    
    print("\n✅ Advanced parsing example completed!")
    print("\nKey features demonstrated:")
    print("- Complex amount format parsing (currency, abbreviations, negatives)")
    print("- Multiple date format support (including Excel serial dates)")
    print("- Robust error handling and validation")
    print("- Type detection combined with format parsing")
    print("- Edge case handling")


if __name__ == "__main__":
    main() 