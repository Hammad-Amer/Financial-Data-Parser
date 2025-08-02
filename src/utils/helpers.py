import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import json


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file exists and is accessible, False otherwise
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    if not validate_file_path(file_path):
        return {'error': f'File not found: {file_path}'}
    
    try:
        stat = os.stat(file_path)
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': stat.st_size,
            'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified_time': datetime.fromtimestamp(stat.st_mtime),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception as e:
        return {'error': f'Error getting file info: {str(e)}'}


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def safe_convert_to_numeric(series: pd.Series) -> pd.Series:
    """
    Safely convert a pandas series to numeric, handling errors gracefully.
    
    Args:
        series: Pandas series to convert
        
    Returns:
        Converted series with errors as NaN
    """
    return pd.to_numeric(series, errors='coerce')


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding
    """
    import chardet
    
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']
    except Exception:
        return 'utf-8'  # Default fallback


def create_summary_report(dataframe: pd.DataFrame, title: str = "Data Summary") -> Dict[str, Any]:
    """
    Create a comprehensive summary report for a DataFrame.
    
    Args:
        dataframe: DataFrame to analyze
        title: Title for the report
        
    Returns:
        Dictionary with summary information
    """
    if dataframe.empty:
        return {'error': 'DataFrame is empty'}
    
    summary = {
        'title': title,
        'timestamp': datetime.now().isoformat(),
        'basic_info': {
            'rows': len(dataframe),
            'columns': len(dataframe.columns),
            'memory_usage_mb': round(dataframe.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            'duplicate_rows': dataframe.duplicated().sum(),
            'null_values': dataframe.isnull().sum().sum()
        },
        'column_info': {},
        'data_types': dataframe.dtypes.to_dict(),
        'sample_data': dataframe.head(5).to_dict('records')
    }
    
    # Analyze each column
    for column in dataframe.columns:
        col_data = dataframe[column]
        col_info = {
            'data_type': str(col_data.dtype),
            'null_count': col_data.isnull().sum(),
            'null_percentage': round((col_data.isnull().sum() / len(col_data)) * 100, 2),
            'unique_values': col_data.nunique()
        }
        
        # Add type-specific information
        if pd.api.types.is_numeric_dtype(col_data):
            col_info.update({
                'min': col_data.min(),
                'max': col_data.max(),
                'mean': col_data.mean(),
                'median': col_data.median(),
                'std': col_data.std()
            })
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            col_info.update({
                'min_date': col_data.min(),
                'max_date': col_data.max(),
                'date_range_days': (col_data.max() - col_data.min()).days
            })
        else:
            # String/object type
            col_info.update({
                'min_length': col_data.astype(str).str.len().min(),
                'max_length': col_data.astype(str).str.len().max(),
                'avg_length': col_data.astype(str).str.len().mean(),
                'most_common': col_data.value_counts().head(3).to_dict()
            })
        
        summary['column_info'][column] = col_info
    
    return summary


def export_summary_to_json(summary: Dict[str, Any], output_path: str) -> bool:
    """
    Export summary report to JSON file.
    
    Args:
        summary: Summary dictionary
        output_path: Path to save the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error exporting summary: {str(e)}")
        return False


def calculate_performance_metrics(func, *args, **kwargs) -> Dict[str, Any]:
    """
    Calculate performance metrics for a function execution.
    
    Args:
        func: Function to measure
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Dictionary with performance metrics
    """
    import time
    import psutil
    import gc
    
    # Get initial memory usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Measure execution time
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = final_memory - initial_memory
    
    # Force garbage collection
    gc.collect()
    
    return {
        'execution_time_seconds': round(end_time - start_time, 4),
        'memory_used_mb': round(memory_used, 2),
        'initial_memory_mb': round(initial_memory, 2),
        'final_memory_mb': round(final_memory, 2),
        'result_type': type(result).__name__,
        'success': True
    }


def validate_dataframe_structure(df: pd.DataFrame, expected_columns: List[str] = None) -> Dict[str, Any]:
    """
    Validate DataFrame structure and data quality.
    
    Args:
        df: DataFrame to validate
        expected_columns: List of expected column names
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'column_count': len(df.columns),
        'row_count': len(df),
        'missing_columns': [],
        'unexpected_columns': []
    }
    
    # Check if DataFrame is empty
    if df.empty:
        validation_result['is_valid'] = False
        validation_result['errors'].append('DataFrame is empty')
        return validation_result
    
    # Check for expected columns
    if expected_columns:
        actual_columns = set(df.columns)
        expected_columns_set = set(expected_columns)
        
        missing_columns = expected_columns_set - actual_columns
        unexpected_columns = actual_columns - expected_columns_set
        
        if missing_columns:
            validation_result['errors'].append(f'Missing columns: {list(missing_columns)}')
            validation_result['missing_columns'] = list(missing_columns)
            validation_result['is_valid'] = False
        
        if unexpected_columns:
            validation_result['warnings'].append(f'Unexpected columns: {list(unexpected_columns)}')
            validation_result['unexpected_columns'] = list(unexpected_columns)
    
    # Check for null values
    null_counts = df.isnull().sum()
    columns_with_nulls = null_counts[null_counts > 0]
    
    if not columns_with_nulls.empty:
        validation_result['warnings'].append(f'Columns with null values: {columns_with_nulls.to_dict()}')
    
    # Check for duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        validation_result['warnings'].append(f'Found {duplicate_count} duplicate rows')
    
    return validation_result 