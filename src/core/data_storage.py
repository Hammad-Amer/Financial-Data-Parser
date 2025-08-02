import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
import sqlite3
from datetime import datetime, date
import json


class DataStorage:
    """
    Optimized data storage system with fast lookup capabilities and efficient querying.
    """
    
    def __init__(self, storage_type: str = 'pandas'):
        """
        Initialize data storage system.
        
        Args:
            storage_type: Type of storage ('pandas', 'sqlite', 'dict')
        """
        self.storage_type = storage_type
        self.data = {}
        self.indexes = {}
        self.metadata = {}
        
        if storage_type == 'sqlite':
            self.db_connection = sqlite3.connect(':memory:')
            self._create_tables()
    
    def store_data(self, dataframe: pd.DataFrame, metadata: Dict[str, Any]) -> str:
        """
        Store data with metadata and create indexes for fast lookup.
        
        Args:
            dataframe: DataFrame to store
            metadata: Metadata about the data (column types, source, etc.)
            
        Returns:
            Dataset identifier
        """
        dataset_id = f"dataset_{len(self.data)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.storage_type == 'pandas':
            self._store_pandas_data(dataset_id, dataframe, metadata)
        elif self.storage_type == 'sqlite':
            self._store_sqlite_data(dataset_id, dataframe, metadata)
        elif self.storage_type == 'dict':
            self._store_dict_data(dataset_id, dataframe, metadata)
        
        return dataset_id
    
    def create_indexes(self, columns: List[str], dataset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create indexes for specified columns to enable fast queries.
        
        Args:
            columns: List of column names to index
            dataset_id: Specific dataset to index (if None, indexes all datasets)
            
        Returns:
            Dictionary with index information
        """
        if dataset_id is None:
            dataset_ids = list(self.data.keys())
        else:
            dataset_ids = [dataset_id]
        
        index_info = {}
        
        for ds_id in dataset_ids:
            if ds_id not in self.data:
                continue
                
            if self.storage_type == 'pandas':
                index_info[ds_id] = self._create_pandas_indexes(ds_id, columns)
            elif self.storage_type == 'sqlite':
                index_info[ds_id] = self._create_sqlite_indexes(ds_id, columns)
            elif self.storage_type == 'dict':
                index_info[ds_id] = self._create_dict_indexes(ds_id, columns)
        
        return index_info
    
    def query_by_criteria(self, filters: Dict[str, Any], dataset_id: Optional[str] = None) -> pd.DataFrame:
        """
        Query data using various criteria with support for range queries.
        
        Args:
            filters: Dictionary with filter criteria
            dataset_id: Specific dataset to query (if None, queries all datasets)
            
        Returns:
            DataFrame with filtered results
        """
        if dataset_id is None:
            # Query all datasets
            results = []
            for ds_id in self.data.keys():
                result = self._query_dataset(ds_id, filters)
                if not result.empty:
                    result['dataset_id'] = ds_id
                    results.append(result)
            
            if results:
                return pd.concat(results, ignore_index=True)
            else:
                return pd.DataFrame()
        else:
            return self._query_dataset(dataset_id, filters)
    
    def aggregate_data(self, group_by: List[str], measures: List[str], dataset_id: Optional[str] = None) -> pd.DataFrame:
        """
        Aggregate data by specified columns with various measures.
        """
        if dataset_id is None:
            # Aggregate all datasets
            all_data = []
            for ds_id in self.data.keys():
                df = self._get_dataset_data(ds_id)
                if not df.empty:
                    df['dataset_id'] = ds_id
                    all_data.append(df)
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                return self._perform_aggregation(combined_df, group_by, measures)
            else:
                # Return empty DataFrame with message
                print("No data available to aggregate.")
                return pd.DataFrame()
        else:
            df = self._get_dataset_data(dataset_id)
            return self._perform_aggregation(df, group_by, measures)
    
    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get information about a specific dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary with dataset information
        """
        if dataset_id not in self.data:
            return {'error': f'Dataset {dataset_id} not found'}
        
        df = self._get_dataset_data(dataset_id)
        
        return {
            'dataset_id': dataset_id,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'metadata': self.metadata.get(dataset_id, {}),
            'indexes': self.indexes.get(dataset_id, {}),
            'storage_type': self.storage_type
        }
    
    def _store_pandas_data(self, dataset_id: str, dataframe: pd.DataFrame, metadata: Dict[str, Any]):
        """Store data using pandas DataFrame."""
        self.data[dataset_id] = dataframe.copy()
        self.metadata[dataset_id] = metadata
        self.indexes[dataset_id] = {}
    
    def _store_sqlite_data(self, dataset_id: str, dataframe: pd.DataFrame, metadata: Dict[str, Any]):
        """Store data using SQLite database."""
        table_name = f"table_{dataset_id}"
        dataframe.to_sql(table_name, self.db_connection, if_exists='replace', index=False)
        
        self.data[dataset_id] = table_name
        self.metadata[dataset_id] = metadata
        self.indexes[dataset_id] = {}
    
    def _store_dict_data(self, dataset_id: str, dataframe: pd.DataFrame, metadata: Dict[str, Any]):
        """Store data using dictionary structure."""
        # Convert DataFrame to dictionary format
        data_dict = {
            'records': dataframe.to_dict('records'),
            'columns': list(dataframe.columns),
            'dtypes': dataframe.dtypes.to_dict()
        }
        
        self.data[dataset_id] = data_dict
        self.metadata[dataset_id] = metadata
        self.indexes[dataset_id] = {}
    
    def _create_pandas_indexes(self, dataset_id: str, columns: List[str]) -> Dict[str, Any]:
        """Create indexes for pandas storage."""
        df = self.data[dataset_id]
        index_info = {}
        
        for column in columns:
            if column in df.columns:
                # Create sorted index for fast lookup
                try:
                    sorted_values = df[column].sort_values()
                    unique_values = sorted_values.unique()
                    value_counts = df[column].value_counts().to_dict()
                    index_info[column] = {
                        'type': 'sorted_index',
                        'unique_values': unique_values,
                        'value_counts': value_counts
                    }
                except TypeError:
                    # Fallback for mixed/unorderable types
                    unique_values = df[column].unique()
                    value_counts = df[column].value_counts().to_dict()
                    index_info[column] = {
                        'type': 'unsorted_index',
                        'unique_values': unique_values,
                        'value_counts': value_counts,
                        'warning': 'Could not sort values due to mixed or unorderable types.'
                    }
        
        self.indexes[dataset_id].update(index_info)
        return index_info
    
    def _create_sqlite_indexes(self, dataset_id: str, columns: List[str]) -> Dict[str, Any]:
        """Create indexes for SQLite storage."""
        table_name = self.data[dataset_id]
        index_info = {}
        
        for column in columns:
            index_name = f"idx_{table_name}_{column}"
            try:
                self.db_connection.execute(f"CREATE INDEX {index_name} ON {table_name} ({column})")
                index_info[column] = {
                    'type': 'sqlite_index',
                    'index_name': index_name
                }
            except Exception as e:
                index_info[column] = {
                    'type': 'sqlite_index',
                    'error': str(e)
                }
        
        self.indexes[dataset_id].update(index_info)
        return index_info
    
    def _create_dict_indexes(self, dataset_id: str, columns: List[str]) -> Dict[str, Any]:
        """Create indexes for dictionary storage."""
        data_dict = self.data[dataset_id]
        records = data_dict['records']
        index_info = {}
        
        for column in columns:
            if column in data_dict['columns']:
                # Create value-based index
                value_index = {}
                for i, record in enumerate(records):
                    value = record.get(column)
                    if value not in value_index:
                        value_index[value] = []
                    value_index[value].append(i)
                
                index_info[column] = {
                    'type': 'dict_index',
                    'value_index': value_index,
                    'unique_values': list(value_index.keys())
                }
        
        self.indexes[dataset_id].update(index_info)
        return index_info
    
    def _query_dataset(self, dataset_id: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Query a specific dataset with filters."""
        if self.storage_type == 'pandas':
            return self._query_pandas_data(dataset_id, filters)
        elif self.storage_type == 'sqlite':
            return self._query_sqlite_data(dataset_id, filters)
        elif self.storage_type == 'dict':
            return self._query_dict_data(dataset_id, filters)
        else:
            return pd.DataFrame()
    
    def _query_pandas_data(self, dataset_id: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Query pandas DataFrame with filters."""
        df = self.data[dataset_id]
        
        for column, condition in filters.items():
            if column not in df.columns:
                continue
            
            if isinstance(condition, dict):
                # Range query
                if 'min' in condition and 'max' in condition:
                    df = df[(df[column] >= condition['min']) & (df[column] <= condition['max'])]
                elif 'min' in condition:
                    df = df[df[column] >= condition['min']]
                elif 'max' in condition:
                    df = df[df[column] <= condition['max']]
                elif 'in' in condition:
                    df = df[df[column].isin(condition['in'])]
            else:
                # Exact match
                df = df[df[column] == condition]
        
        return df
    
    def _query_sqlite_data(self, dataset_id: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Query SQLite data with filters."""
        table_name = self.data[dataset_id]
        
        # Build WHERE clause
        where_conditions = []
        for column, condition in filters.items():
            if isinstance(condition, dict):
                # Range query
                if 'min' in condition and 'max' in condition:
                    where_conditions.append(f"{column} BETWEEN {condition['min']} AND {condition['max']}")
                elif 'min' in condition:
                    where_conditions.append(f"{column} >= {condition['min']}")
                elif 'max' in condition:
                    where_conditions.append(f"{column} <= {condition['max']}")
                elif 'in' in condition:
                    values = ','.join([f"'{v}'" for v in condition['in']])
                    where_conditions.append(f"{column} IN ({values})")
            else:
                # Exact match
                if isinstance(condition, str):
                    where_conditions.append(f"{column} = '{condition}'")
                else:
                    where_conditions.append(f"{column} = {condition}")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        query = f"SELECT * FROM {table_name} WHERE {where_clause}"
        
        return pd.read_sql_query(query, self.db_connection)
    
    def _query_dict_data(self, dataset_id: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Query dictionary data with filters."""
        data_dict = self.data[dataset_id]
        records = data_dict['records']
        
        filtered_records = []
        for record in records:
            match = True
            for column, condition in filters.items():
                if column not in record:
                    match = False
                    break
                
                value = record[column]
                
                if isinstance(condition, dict):
                    # Range query
                    if 'min' in condition and value < condition['min']:
                        match = False
                    elif 'max' in condition and value > condition['max']:
                        match = False
                    elif 'in' in condition and value not in condition['in']:
                        match = False
                else:
                    # Exact match
                    if value != condition:
                        match = False
                
                if not match:
                    break
            
            if match:
                filtered_records.append(record)
        
        return pd.DataFrame(filtered_records)
    
    def _get_dataset_data(self, dataset_id: str) -> pd.DataFrame:
        """Get DataFrame for a specific dataset."""
        if self.storage_type == 'pandas':
            return self.data[dataset_id]
        elif self.storage_type == 'sqlite':
            table_name = self.data[dataset_id]
            return pd.read_sql_query(f"SELECT * FROM {table_name}", self.db_connection)
        elif self.storage_type == 'dict':
            data_dict = self.data[dataset_id]
            return pd.DataFrame(data_dict['records'])
        else:
            return pd.DataFrame()
    
    def _perform_aggregation(self, df: pd.DataFrame, group_by: List[str], measures: List[str]) -> pd.DataFrame:
        """Perform aggregation on DataFrame."""
        if df.empty:
            print("No data available to aggregate.")
            return pd.DataFrame()
        # Validate group_by and measures columns
        missing_group = [col for col in group_by if col and col not in df.columns]
        missing_measures = [m.split(':')[0] if ':' in m else m for m in measures if m and (m.split(':')[0] if ':' in m else m) not in df.columns]
        if missing_group or missing_measures:
            print(f"Missing columns for aggregation. Group by: {missing_group}, Measures: {missing_measures}")
            return pd.DataFrame()
        # Define aggregation functions
        agg_functions = {}
        for measure in measures:
            if ':' in measure:
                col_name, agg_func = measure.split(':')
                if agg_func in ['sum', 'mean', 'count', 'min', 'max']:
                    agg_functions[col_name] = agg_func
                else:
                    agg_functions[col_name] = 'sum'  # Default
            else:
                agg_functions[measure] = 'sum'  # Default
        # Perform aggregation
        if group_by:
            result = df.groupby(group_by).agg(agg_functions).reset_index()
        else:
            result = df.agg(agg_functions).to_frame().T
        return result
    
    def _create_tables(self):
        """Create SQLite tables if using SQLite storage."""
        pass  # Tables will be created dynamically when data is stored
