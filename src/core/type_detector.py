import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import re
from datetime import datetime
import dateutil.parser
from decimal import Decimal, InvalidOperation


class DataTypeDetector:
    """
    Intelligently detects and classifies data types in columns.
    """
    
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY, DD/MM/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
            r'\d{1,2}-\w{3}-\d{2,4}',    # DD-MON-YYYY
            r'Q[1-4]\s+\d{4}',           # Quarter 1 2024
            r'Q[1-4]-\d{2}',             # Q1-24
            r'\w{3}\s+\d{4}',            # Mar 2024
            r'\w+\s+\d{4}',              # March 2024
        ]
        
        self.number_patterns = [
            r'^\$[\d,]+\.?\d*$',         # $1,234.56
            r'^€[\d.,]+$',               # €1.234,56
            r'^₹[\d,]+\.?\d*$',          # ₹1,23,456.78
            r'^\([\d,]+\.?\d*\)$',       # (1,234.56)
            r'^[\d,]+\.?\d*-$',          # 1234.56-
            r'^[\d.]+[KMB]$',            # 1.23K, 2.5M, 1.2B
        ]
    
    def analyze_column(self, data: pd.Series) -> Dict[str, Any]:
        """
        Analyze a column and determine its data type with confidence scores.
        
        Args:
            data: Pandas Series containing column data
            
        Returns:
            Dictionary with detected type and confidence scores
        """
        # Remove null values for analysis
        clean_data = data.dropna()
        
        if len(clean_data) == 0:
            return {
                'type': 'unknown',
                'confidence': 0.0,
                'scores': {'string': 0.0, 'number': 0.0, 'date': 0.0}
            }
        
        # Convert to string for pattern matching
        str_data = clean_data.astype(str)
        
        # Try parsing as dates first
        date_score = self._detect_date_format(str_data)
        
        # Try parsing as numbers
        number_score = self._detect_number_format(str_data)
        
        # Calculate string score (what's left after date and number detection)
        string_score = max(0, 1.0 - date_score - number_score)
        
        # Simple logic: if we have a clear winner, use it
        # Otherwise, default to string for mixed data
        if date_score > 0.5:
            # Clear date dominance
            date_score = 1.0
            number_score = 0.0
            string_score = 0.0
        elif number_score > 0.5:
            # Clear number dominance
            date_score = 0.0
            number_score = 1.0
            string_score = 0.0
        else:
            # Mixed or unclear - default to string
            date_score = 0.0
            number_score = 0.0
            string_score = 1.0
        
        scores = {
            'string': string_score,
            'number': number_score,
            'date': date_score
        }
        
        # Determine the most likely type
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        return {
            'type': best_type,
            'confidence': confidence,
            'scores': scores,
            'format_info': self._get_format_info(str_data, best_type)
        }
    
    def detect_date_format(self, sample_values: pd.Series) -> Dict[str, Any]:
        """
        Detect date format from sample values.
        
        Args:
            sample_values: Series of string values to analyze
            
        Returns:
            Dictionary with detected date format information
        """
        date_formats = []
        excel_dates = []
        
        for value in sample_values:
            # Check for Excel serial dates
            try:
                float_val = float(value)
                if 1 <= float_val <= 100000:  # Reasonable Excel date range
                    excel_dates.append(float_val)
            except ValueError:
                pass
            
            # Check for various date patterns
            for pattern in self.date_patterns:
                if re.match(pattern, str(value), re.IGNORECASE):
                    date_formats.append(pattern)
                    break
        
        return {
            'detected_patterns': list(set(date_formats)),
            'excel_serial_dates': len(excel_dates) > 0,
            'excel_date_count': len(excel_dates),
            'sample_excel_dates': excel_dates[:5] if excel_dates else []
        }
    
    def detect_number_format(self, sample_values: pd.Series) -> Dict[str, Any]:
        """
        Detect number format from sample values.
        
        Args:
            sample_values: Series of string values to analyze
            
        Returns:
            Dictionary with detected number format information
        """
        currency_symbols = []
        decimal_separators = []
        thousand_separators = []
        negative_formats = []
        
        for value in sample_values:
            # Check for currency symbols
            if re.search(r'[\$€₹£¥]', str(value)):
                currency_symbols.append(re.search(r'[\$€₹£¥]', str(value)).group())
            
            # Check for decimal separators
            if re.search(r'[.,]', str(value)):
                decimal_sep = re.search(r'[.,]', str(value)).group()
                decimal_separators.append(decimal_sep)
            
            # Check for thousand separators
            if re.search(r'[\d,]+', str(value)):
                thousand_sep = re.search(r'[\d,]+', str(value)).group()
                if ',' in thousand_sep:
                    thousand_separators.append(',')
            
            # Check for negative formats
            if re.search(r'\(.*\)', str(value)) or str(value).endswith('-'):
                negative_formats.append(str(value))
        
        return {
            'currency_symbols': list(set(currency_symbols)),
            'decimal_separators': list(set(decimal_separators)),
            'thousand_separators': list(set(thousand_separators)),
            'negative_formats': list(set(negative_formats)),
            'abbreviated_formats': any(re.search(r'[KMB]$', str(v)) for v in sample_values)
        }
    
    def classify_string_type(self, sample_values: pd.Series) -> Dict[str, Any]:
        """
        Classify string data into subtypes.
        
        Args:
            sample_values: Series of string values to analyze
            
        Returns:
            Dictionary with string classification information
        """
        # Analyze string patterns
        account_patterns = []
        transaction_patterns = []
        company_patterns = []
        
        for value in sample_values:
            value_str = str(value).lower()
            
            # Account-related patterns
            if any(word in value_str for word in ['account', 'acc', 'ledger', 'gl']):
                account_patterns.append(value)
            
            # Transaction-related patterns
            if any(word in value_str for word in ['transaction', 'ref', 'invoice', 'payment']):
                transaction_patterns.append(value)
            
            # Company-related patterns
            if any(word in value_str for word in ['inc', 'corp', 'ltd', 'company', 'co']):
                company_patterns.append(value)
        
        return {
            'account_related': len(account_patterns),
            'transaction_related': len(transaction_patterns),
            'company_related': len(company_patterns),
            'sample_accounts': account_patterns[:3],
            'sample_transactions': transaction_patterns[:3],
            'sample_companies': company_patterns[:3]
        }
    
    def _detect_date_format(self, str_data: pd.Series) -> float:
        """
        Calculate confidence score for date detection.
        
        Args:
            str_data: Series of string values
            
        Returns:
            Confidence score between 0 and 1
        """
        date_count = 0
        total_count = len(str_data)
        
        for value in str_data:
            value_str = str(value).strip()
            
            # Check for Excel serial dates (much more restrictive)
            try:
                float_val = float(value_str)
                # Only consider as Excel date if it's an integer in a reasonable date range
                if float_val == int(float_val):  # Must be integer
                    # Excel dates: 1 = Jan 1, 1900, 73050 = Dec 31, 2099
                    # But be more restrictive - only consider if it's in a reasonable range
                    if 1000 <= float_val <= 73050:  # More reasonable range
                        date_count += 1
                        continue
            except ValueError:
                pass
            
            # Check for date patterns (more specific)
            for pattern in self.date_patterns:
                if re.match(pattern, value_str, re.IGNORECASE):
                    date_count += 1
                    break
        
        return date_count / total_count if total_count > 0 else 0.0
    
    def _detect_number_format(self, str_data: pd.Series) -> float:
        """
        Calculate confidence score for number detection.
        
        Args:
            str_data: Series of string values
            
        Returns:
            Confidence score between 0 and 1
        """
        number_count = 0
        total_count = len(str_data)
        
        for value in str_data:
            value_str = str(value).strip()
            
            # Skip if it looks like a date first
            is_date = False
            for pattern in self.date_patterns:
                if re.match(pattern, value_str, re.IGNORECASE):
                    is_date = True
                    break
            
            if is_date:
                continue  # Skip date-like values
            
            # Try to parse as number
            try:
                # Remove common currency symbols and separators
                clean_value = re.sub(r'[\$€₹£¥,()]', '', value_str)
                clean_value = clean_value.replace('-', '')
                
                # Try parsing as float
                float(clean_value)
                number_count += 1
                continue
            except ValueError:
                pass
            
            # Check for abbreviated formats (K, M, B)
            if re.match(r'^[\d.]+[KMB]$', value_str, re.IGNORECASE):
                number_count += 1
                continue
        
        return number_count / total_count if total_count > 0 else 0.0
    
    def _get_format_info(self, str_data: pd.Series, detected_type: str) -> Dict[str, Any]:
        """
        Get detailed format information for the detected type.
        
        Args:
            str_data: Series of string values
            detected_type: The detected data type
            
        Returns:
            Dictionary with format information
        """
        if detected_type == 'date':
            return self.detect_date_format(str_data)
        elif detected_type == 'number':
            return self.detect_number_format(str_data)
        else:
            return self.classify_string_type(str_data)
