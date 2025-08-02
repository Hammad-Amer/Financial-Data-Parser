import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
import re
from datetime import datetime, date
import dateutil.parser
from decimal import Decimal, InvalidOperation
import locale


class FormatParser:
    """
    Handles parsing of complex financial data formats including amounts and dates.
    """
    
    def __init__(self):
        self.currency_symbols = {
            '$': 'USD',
            '€': 'EUR', 
            '₹': 'INR',
            '£': 'GBP',
            '¥': 'JPY'
        }
        
        self.abbreviation_multipliers = {
            'K': 1000,
            'M': 1000000,
            'B': 1000000000,
            'T': 1000000000000
        }
        
        # Date format patterns
        self.date_patterns = {
            'MM/DD/YYYY': r'(\d{1,2})/(\d{1,2})/(\d{4})',
            'DD/MM/YYYY': r'(\d{1,2})/(\d{1,2})/(\d{4})',
            'YYYY-MM-DD': r'(\d{4})-(\d{1,2})-(\d{1,2})',
            'DD-MON-YYYY': r'(\d{1,2})-(\w{3})-(\d{4})',
            'Quarter': r'Q([1-4])\s+(\d{4})',
            'Month-Year': r'(\w+)\s+(\d{4})'
        }
    
    def parse_amount(self, value: Any, detected_format: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Parse amount values with various formats.
        
        Args:
            value: The value to parse
            detected_format: Optional format information from type detection
            
        Returns:
            Dictionary with parsed amount information
        """
        if pd.isna(value) or value == '':
            return {'parsed_value': None, 'currency': None, 'is_negative': False, 'error': 'Empty value'}
        
        str_value = str(value).strip()
        
        try:
            # Handle special formats
            if self._is_special_format(str_value):
                return self._handle_special_formats(str_value)
            
            # Normalize currency
            normalized_value = self.normalize_currency(str_value)
            
            # Parse the normalized value
            parsed_result = self._parse_normalized_amount(normalized_value)
            
            return parsed_result
            
        except Exception as e:
            return {
                'parsed_value': None,
                'currency': None,
                'is_negative': False,
                'error': f'Parse error: {str(e)}',
                'original_value': str_value
            }
    
    def parse_date(self, value: Any, detected_format: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Parse date values with various formats.
        
        Args:
            value: The value to parse
            detected_format: Optional format information from type detection
            
        Returns:
            Dictionary with parsed date information
        """
        if pd.isna(value) or value == '':
            return {'parsed_value': None, 'format': None, 'error': 'Empty value'}
        
        str_value = str(value).strip()
        
        try:
            # Check for Excel serial date
            if self._is_excel_serial_date(str_value):
                return self._parse_excel_serial_date(str_value)
            
            # Try parsing with dateutil first
            try:
                parsed_date = dateutil.parser.parse(str_value)
                return {
                    'parsed_value': parsed_date,
                    'format': 'dateutil_parsed',
                    'year': parsed_date.year,
                    'month': parsed_date.month,
                    'day': parsed_date.day
                }
            except:
                pass
            
            # Try specific date patterns
            for pattern_name, pattern in self.date_patterns.items():
                match = re.match(pattern, str_value, re.IGNORECASE)
                if match:
                    return self._parse_date_pattern(pattern_name, match, str_value)
            
            # Try quarter format
            if 'Q' in str_value.upper():
                return self._parse_quarter_format(str_value)
            
            # Try month-year format
            if re.match(r'\w+\s+\d{4}', str_value, re.IGNORECASE):
                return self._parse_month_year_format(str_value)
            
            return {
                'parsed_value': None,
                'format': None,
                'error': f'Unrecognized date format: {str_value}',
                'original_value': str_value
            }
            
        except Exception as e:
            return {
                'parsed_value': None,
                'format': None,
                'error': f'Parse error: {str(e)}',
                'original_value': str_value
            }
    
    def normalize_currency(self, value: str) -> str:
        """
        Normalize currency symbols and separators.
        
        Args:
            value: String value to normalize
            
        Returns:
            Normalized string
        """
        # Remove currency symbols for parsing
        normalized = value
        
        # Handle European format (comma as decimal separator)
        if re.search(r'[\d,]+\.\d{3}', normalized):
            # European format: 1.234,56 -> 1234.56
            normalized = re.sub(r'(\d+)\.(\d{3})', r'\1\2', normalized)
            normalized = normalized.replace(',', '.')
        
        # Remove thousand separators
        normalized = re.sub(r'(\d),(\d{3})', r'\1\2', normalized)
        
        return normalized
    
    def handle_special_formats(self, value: str) -> Dict[str, Any]:
        """
        Handle special amount formats like abbreviated values.
        
        Args:
            value: String value to parse
            
        Returns:
            Dictionary with parsed information
        """
        # Check for abbreviated formats (K, M, B, T)
        for abbrev, multiplier in self.abbreviation_multipliers.items():
            if value.upper().endswith(abbrev):
                try:
                    # Extract the numeric part
                    numeric_part = value[:-1] if len(value) > 1 else value
                    base_value = float(numeric_part)
                    final_value = base_value * multiplier
                    
                    return {
                        'parsed_value': final_value,
                        'currency': None,
                        'is_negative': False,
                        'abbreviation': abbrev,
                        'multiplier': multiplier,
                        'base_value': base_value
                    }
                except ValueError:
                    pass
        
        # Handle negative in parentheses
        if value.startswith('(') and value.endswith(')'):
            try:
                inner_value = value[1:-1]
                parsed_value = float(self.normalize_currency(inner_value))
                return {
                    'parsed_value': abs(parsed_value),
                    'currency': None,
                    'is_negative': True,
                    'format': 'parentheses_negative'
                }
            except ValueError:
                pass
        
        # Handle trailing negative
        if value.endswith('-'):
            try:
                base_value = value[:-1]
                parsed_value = float(self.normalize_currency(base_value))
                return {
                    'parsed_value': abs(parsed_value),
                    'currency': None,
                    'is_negative': True,
                    'format': 'trailing_negative'
                }
            except ValueError:
                pass
        
        return {
            'parsed_value': None,
            'currency': None,
            'is_negative': False,
            'error': f'Unrecognized special format: {value}'
        }
    
    def _is_special_format(self, value: str) -> bool:
        """Check if value is in a special format."""
        # Check for abbreviated formats
        if any(value.upper().endswith(abbrev) for abbrev in self.abbreviation_multipliers.keys()):
            return True
        
        # Check for parentheses negative
        if value.startswith('(') and value.endswith(')'):
            return True
        
        # Check for trailing negative
        if value.endswith('-'):
            return True
        
        return False
    
    def _handle_special_formats(self, value: str) -> Dict[str, Any]:
        """Handle special format parsing."""
        return self.handle_special_formats(value)
    
    def _parse_normalized_amount(self, normalized_value: str) -> Dict[str, Any]:
        """Parse normalized amount value."""
        try:
            # Extract currency symbol if present
            currency = None
            for symbol, code in self.currency_symbols.items():
                if symbol in normalized_value:
                    currency = code
                    break
            
            # Remove currency symbols for numeric parsing
            clean_value = re.sub(r'[\$€₹£¥]', '', normalized_value)
            
            # Parse as float
            parsed_value = float(clean_value)
            
            return {
                'parsed_value': abs(parsed_value),
                'currency': currency,
                'is_negative': parsed_value < 0,
                'format': 'standard'
            }
            
        except ValueError as e:
            return {
                'parsed_value': None,
                'currency': None,
                'is_negative': False,
                'error': f'Invalid numeric format: {str(e)}'
            }
    
    def _is_excel_serial_date(self, value: str) -> bool:
        """Check if value is an Excel serial date."""
        try:
            float_val = float(value)
            return 1 <= float_val <= 100000  # Reasonable Excel date range
        except ValueError:
            return False
    
    def _parse_excel_serial_date(self, value: str) -> Dict[str, Any]:
        """Parse Excel serial date."""
        try:
            serial_date = float(value)
            # Excel dates are days since 1900-01-01
            # But Excel incorrectly treats 1900 as a leap year
            # So we need to adjust for dates after 1900-02-28
            if serial_date > 59:  # After 1900-02-28
                serial_date -= 1
            
            # Convert to datetime
            base_date = datetime(1900, 1, 1)
            parsed_date = base_date + pd.Timedelta(days=serial_date - 1)
            
            return {
                'parsed_value': parsed_date,
                'format': 'excel_serial',
                'serial_date': serial_date,
                'year': parsed_date.year,
                'month': parsed_date.month,
                'day': parsed_date.day
            }
        except Exception as e:
            return {
                'parsed_value': None,
                'format': 'excel_serial',
                'error': f'Invalid Excel serial date: {str(e)}'
            }
    
    def _parse_date_pattern(self, pattern_name: str, match, original_value: str) -> Dict[str, Any]:
        """Parse date using specific pattern."""
        try:
            if pattern_name == 'MM/DD/YYYY':
                month, day, year = match.groups()
                parsed_date = datetime(int(year), int(month), int(day))
            elif pattern_name == 'DD/MM/YYYY':
                day, month, year = match.groups()
                parsed_date = datetime(int(year), int(month), int(day))
            elif pattern_name == 'YYYY-MM-DD':
                year, month, day = match.groups()
                parsed_date = datetime(int(year), int(month), int(day))
            elif pattern_name == 'DD-MON-YYYY':
                day, month, year = match.groups()
                # Convert month abbreviation to number
                month_num = self._month_abbrev_to_num(month)
                parsed_date = datetime(int(year), month_num, int(day))
            else:
                return {
                    'parsed_value': None,
                    'format': pattern_name,
                    'error': f'Unsupported pattern: {pattern_name}'
                }
            
            return {
                'parsed_value': parsed_date,
                'format': pattern_name,
                'year': parsed_date.year,
                'month': parsed_date.month,
                'day': parsed_date.day
            }
            
        except Exception as e:
            return {
                'parsed_value': None,
                'format': pattern_name,
                'error': f'Parse error: {str(e)}',
                'original_value': original_value
            }
    
    def _parse_quarter_format(self, value: str) -> Dict[str, Any]:
        """Parse quarter format (Q1 2024, Q1-24)."""
        try:
            # Handle Q1 2024 format
            quarter_match = re.match(r'Q([1-4])\s+(\d{4})', value, re.IGNORECASE)
            if quarter_match:
                quarter, year = quarter_match.groups()
                quarter = int(quarter)
                year = int(year)
                
                # Calculate month for quarter start
                month = (quarter - 1) * 3 + 1
                parsed_date = datetime(year, month, 1)
                
                return {
                    'parsed_value': parsed_date,
                    'format': 'quarter',
                    'quarter': quarter,
                    'year': year,
                    'month': month,
                    'day': 1
                }
            
            # Handle Q1-24 format
            quarter_match = re.match(r'Q([1-4])-(\d{2})', value, re.IGNORECASE)
            if quarter_match:
                quarter, year_short = quarter_match.groups()
                quarter = int(quarter)
                year = 2000 + int(year_short)  # Assume 20xx
                
                month = (quarter - 1) * 3 + 1
                parsed_date = datetime(year, month, 1)
                
                return {
                    'parsed_value': parsed_date,
                    'format': 'quarter_short',
                    'quarter': quarter,
                    'year': year,
                    'month': month,
                    'day': 1
                }
            
            return {
                'parsed_value': None,
                'format': 'quarter',
                'error': f'Invalid quarter format: {value}'
            }
            
        except Exception as e:
            return {
                'parsed_value': None,
                'format': 'quarter',
                'error': f'Parse error: {str(e)}',
                'original_value': value
            }
    
    def _parse_month_year_format(self, value: str) -> Dict[str, Any]:
        """Parse month-year format (Mar 2024, March 2024)."""
        try:
            # Extract month and year
            parts = value.split()
            if len(parts) >= 2:
                month_str = parts[0]
                year_str = parts[1]
                
                month_num = self._month_name_to_num(month_str)
                year = int(year_str)
                
                parsed_date = datetime(year, month_num, 1)
                
                return {
                    'parsed_value': parsed_date,
                    'format': 'month_year',
                    'month_name': month_str,
                    'month': month_num,
                    'year': year,
                    'day': 1
                }
            
            return {
                'parsed_value': None,
                'format': 'month_year',
                'error': f'Invalid month-year format: {value}'
            }
            
        except Exception as e:
            return {
                'parsed_value': None,
                'format': 'month_year',
                'error': f'Parse error: {str(e)}',
                'original_value': value
            }
    
    def _month_abbrev_to_num(self, month_abbrev: str) -> int:
        """Convert month abbreviation to number."""
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        return month_map.get(month_abbrev.lower(), 1)
    
    def _month_name_to_num(self, month_name: str) -> int:
        """Convert month name to number."""
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return month_map.get(month_name.lower(), 1)
