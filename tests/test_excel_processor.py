import unittest
import pandas as pd
import tempfile
import os
from src.core.excel_processor import ExcelProcessor


class TestExcelProcessor(unittest.TestCase):
    """Test cases for ExcelProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ExcelProcessor()
        
        # Create a temporary Excel file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        self.temp_file.close()
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        # Save to Excel file
        with pd.ExcelWriter(self.temp_file.name, engine='openpyxl') as writer:
            self.sample_data.to_excel(writer, sheet_name='Sheet1', index=False)
            self.sample_data.to_excel(writer, sheet_name='Sheet2', index=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_files(self):
        """Test loading Excel files."""
        # Test loading a single file
        file_info = self.processor.load_files([self.temp_file.name])
        
        self.assertIn(self.temp_file.name, file_info)
        self.assertEqual(file_info[self.temp_file.name]['sheet_count'], 2)
        self.assertIn('Sheet1', file_info[self.temp_file.name]['sheets'])
        self.assertIn('Sheet2', file_info[self.temp_file.name]['sheets'])
    
    def test_load_files_file_not_found(self):
        """Test loading non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.processor.load_files(['non_existent_file.xlsx'])
    
    def test_get_sheet_info(self):
        """Test getting sheet information."""
        # Load file first
        self.processor.load_files([self.temp_file.name])
        
        # Get sheet info
        sheet_info = self.processor.get_sheet_info(self.temp_file.name)
        
        self.assertIn('Sheet1', sheet_info)
        self.assertIn('Sheet2', sheet_info)
        self.assertEqual(sheet_info['Sheet1']['column_count'], 3)
        self.assertEqual(sheet_info['Sheet1']['sample_rows'], 5)
    
    def test_get_sheet_info_file_not_loaded(self):
        """Test getting sheet info for unloaded file."""
        with self.assertRaises(ValueError):
            self.processor.get_sheet_info('unloaded_file.xlsx')
    
    def test_extract_data(self):
        """Test extracting data from sheet."""
        # Load file first
        self.processor.load_files([self.temp_file.name])
        
        # Extract data from first sheet
        df = self.processor.extract_data(self.temp_file.name, 'Sheet1')
        
        self.assertEqual(len(df), 5)
        self.assertEqual(len(df.columns), 3)
        self.assertListEqual(list(df.columns), ['A', 'B', 'C'])
    
    def test_extract_data_invalid_sheet(self):
        """Test extracting data from invalid sheet."""
        # Load file first
        self.processor.load_files([self.temp_file.name])
        
        with self.assertRaises(ValueError):
            self.processor.extract_data(self.temp_file.name, 'InvalidSheet')
    
    def test_preview_data(self):
        """Test previewing data."""
        # Load file first
        self.processor.load_files([self.temp_file.name])
        
        # Preview data
        df = self.processor.preview_data(self.temp_file.name, 'Sheet1', rows=3)
        
        self.assertEqual(len(df), 3)
        self.assertEqual(len(df.columns), 3)
    
    def test_get_all_sheets_data(self):
        """Test getting data from all sheets."""
        # Load file first
        self.processor.load_files([self.temp_file.name])
        
        # Get all sheets data
        all_data = self.processor.get_all_sheets_data(self.temp_file.name)
        
        self.assertIn('Sheet1', all_data)
        self.assertIn('Sheet2', all_data)
        self.assertEqual(len(all_data['Sheet1']), 5)
        self.assertEqual(len(all_data['Sheet2']), 5)


if __name__ == '__main__':
    unittest.main() 