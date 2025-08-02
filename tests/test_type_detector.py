import unittest
import pandas as pd
import numpy as np
from src.core.type_detector import DataTypeDetector


class TestDataTypeDetector(unittest.TestCase):
    """Test cases for DataTypeDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = DataTypeDetector()
    
    def test_analyze_column_numeric(self):
        """Test analyzing numeric column."""
        # Create numeric data
        data = pd.Series([1, 2, 3, 4, 5, 10.5, 20.7, 30.2])
        
        result = self.detector.analyze_column(data)
        
        self.assertEqual(result['type'], 'number')
        self.assertGreater(result['confidence'], 0.8)
        self.assertIn('number', result['scores'])
        self.assertIn('date', result['scores'])
        self.assertIn('string', result['scores'])
    
    def test_analyze_column_string(self):
        """Test analyzing string column."""
        # Create string data
        data = pd.Series(['apple', 'banana', 'cherry', 'date', 'elderberry'])
        
        result = self.detector.analyze_column(data)
        
        self.assertEqual(result['type'], 'string')
        self.assertGreater(result['confidence'], 0.8)
    
    def test_analyze_column_date(self):
        """Test analyzing date column."""
        # Create date data
        data = pd.Series(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'])
        
        result = self.detector.analyze_column(data)
        
        self.assertEqual(result['type'], 'date')
        self.assertGreater(result['confidence'], 0.8)
    
    def test_analyze_column_mixed(self):
        """Test analyzing mixed data column."""
        # Create mixed data
        data = pd.Series(['text', 123, 'more text', 456, 'final text'])
        
        result = self.detector.analyze_column(data)
        
        # Should default to string for mixed data
        self.assertEqual(result['type'], 'string')
    
    def test_analyze_column_empty(self):
        """Test analyzing empty column."""
        # Create empty data
        data = pd.Series([])
        
        result = self.detector.analyze_column(data)
        
        self.assertEqual(result['type'], 'unknown')
        self.assertEqual(result['confidence'], 0.0)
    
    def test_analyze_column_with_nulls(self):
        """Test analyzing column with null values."""
        # Create data with nulls
        data = pd.Series([1, 2, np.nan, 4, 5, np.nan, 7])
        
        result = self.detector.analyze_column(data)
        
        self.assertEqual(result['type'], 'number')
        self.assertGreater(result['confidence'], 0.5)
    
    def test_detect_date_format(self):
        """Test date format detection."""
        # Test various date formats
        sample_values = pd.Series([
            '2023-01-01',
            '01/15/2023',
            'Q1 2023',
            'Dec 2023',
            '44927'  # Excel serial date
        ])
        
        result = self.detector.detect_date_format(sample_values)
        
        self.assertIn('detected_patterns', result)
        self.assertIn('excel_serial_dates', result)
        self.assertIn('excel_date_count', result)
    
    def test_detect_number_format(self):
        """Test number format detection."""
        # Test various number formats
        sample_values = pd.Series([
            '$1,234.56',
            '€1.234,56',
            '(500.00)',
            '1.5M',
            '₹1,23,456'
        ])
        
        result = self.detector.detect_number_format(sample_values)
        
        self.assertIn('currency_symbols', result)
        self.assertIn('decimal_separators', result)
        self.assertIn('thousand_separators', result)
        self.assertIn('negative_formats', result)
        self.assertIn('abbreviated_formats', result)
    
    def test_classify_string_type(self):
        """Test string type classification."""
        # Test account-related strings
        account_values = pd.Series([
            'Account 123',
            'GL Account',
            'Ledger Entry',
            'General Ledger'
        ])
        
        result = self.detector.classify_string_type(account_values)
        
        self.assertIn('account_related', result)
        self.assertIn('transaction_related', result)
        self.assertIn('company_related', result)
    
    def test_detect_date_format_with_excel_serial(self):
        """Test date format detection with Excel serial dates."""
        # Test Excel serial dates
        sample_values = pd.Series(['44927', '44928', '44929'])
        
        result = self.detector.detect_date_format(sample_values)
        
        self.assertTrue(result['excel_serial_dates'])
        self.assertEqual(result['excel_date_count'], 3)
    
    def test_detect_number_format_with_currencies(self):
        """Test number format detection with various currencies."""
        # Test different currency formats
        sample_values = pd.Series([
            '$1,234.56',
            '€1.234,56',
            '₹1,23,456.78',
            '£1,234.56',
            '¥1,234'
        ])
        
        result = self.detector.detect_number_format(sample_values)
        
        self.assertIn('$', result['currency_symbols'])
        self.assertIn('€', result['currency_symbols'])
        self.assertIn('₹', result['currency_symbols'])
    
    def test_confidence_scoring(self):
        """Test confidence scoring for different data types."""
        # Test numeric data
        numeric_data = pd.Series([1, 2, 3, 4, 5])
        numeric_result = self.detector.analyze_column(numeric_data)
        
        # Test string data
        string_data = pd.Series(['a', 'b', 'c', 'd', 'e'])
        string_result = self.detector.analyze_column(string_data)
        
        # Test date data
        date_data = pd.Series(['2023-01-01', '2023-01-02', '2023-01-03'])
        date_result = self.detector.analyze_column(date_data)
        
        # Verify confidence scores are reasonable
        self.assertGreater(numeric_result['confidence'], 0.5)
        self.assertGreater(string_result['confidence'], 0.5)
        self.assertGreater(date_result['confidence'], 0.5)
        
        # Verify scores sum to approximately 1
        numeric_scores = numeric_result['scores']
        self.assertAlmostEqual(sum(numeric_scores.values()), 1.0, places=1)


if __name__ == '__main__':
    unittest.main()
