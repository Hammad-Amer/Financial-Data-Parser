#!/usr/bin/env python3
"""
Performance Demo for Financial Data Parser

This example demonstrates:
- Phase 4: Data storage optimization
- Multiple storage strategies
- Performance benchmarking
- Query optimization
- Aggregation capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.excel_processor import ExcelProcessor
from src.core.data_storage import DataStorage
from src.core.type_detector import DataTypeDetector
from src.utils.helpers import calculate_performance_metrics, create_summary_report
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_sample_financial_data(size: int = 10000) -> pd.DataFrame:
    """Create sample financial data for testing."""
    print(f"Creating sample financial data with {size:,} records...")
    
    np.random.seed(42)  # For reproducible results
    
    # Generate sample data
    data = {
        'transaction_id': range(1, size + 1),
        'date': pd.date_range(start='2023-01-01', periods=size, freq='D'),
        'account_name': np.random.choice(['Cash', 'Accounts Receivable', 'Inventory', 'Equipment'], size),
        'description': [f'Transaction {i}' for i in range(1, size + 1)],
        'amount': np.random.normal(1000, 500, size),
        'currency': np.random.choice(['USD', 'EUR', 'GBP'], size),
        'category': np.random.choice(['Revenue', 'Expense', 'Asset', 'Liability'], size),
        'reference': [f'REF-{i:06d}' for i in range(1, size + 1)]
    }
    
    # Add some formatted amounts
    data['formatted_amount'] = [
        f"${abs(amt):,.2f}" if amt >= 0 else f"({abs(amt):,.2f})"
        for amt in data['amount']
    ]
    
    # Add some date variations
    data['quarter'] = [f"Q{(i % 4) + 1} 2023" for i in range(size)]
    data['month_year'] = [f"{datetime(2023, (i % 12) + 1, 1).strftime('%b %Y')}" for i in range(size)]
    
    df = pd.DataFrame(data)
    print(f"✅ Created sample data: {df.shape}")
    return df


def benchmark_storage_strategies(df: pd.DataFrame):
    """Benchmark different storage strategies."""
    print("\n=== Storage Strategy Benchmarking ===")
    print("=" * 50)
    
    storage_strategies = ['pandas', 'sqlite', 'dict']
    results = {}
    
    for strategy in storage_strategies:
        print(f"\n📊 Testing {strategy.upper()} storage strategy...")
        
        # Measure storage performance
        def store_data():
            storage = DataStorage(storage_type=strategy)
            dataset_id = storage.store_data(df, {'source': 'sample', 'strategy': strategy})
            return storage, dataset_id
        
        metrics = calculate_performance_metrics(store_data)
        results[strategy] = metrics
        
        print(f"   ⏱️  Storage time: {metrics['execution_time_seconds']:.4f}s")
        print(f"   💾 Memory used: {metrics['memory_used_mb']:.2f} MB")
        print(f"   📈 Final memory: {metrics['final_memory_mb']:.2f} MB")
    
    # Compare results
    print("\n📊 Storage Strategy Comparison:")
    print("-" * 40)
    for strategy, metrics in results.items():
        print(f"{strategy.upper():>10}: {metrics['execution_time_seconds']:>8.4f}s | {metrics['memory_used_mb']:>8.2f}MB")
    
    return results


def benchmark_query_performance(df: pd.DataFrame):
    """Benchmark query performance across storage strategies."""
    print("\n=== Query Performance Benchmarking ===")
    print("=" * 50)
    
    storage_strategies = ['pandas', 'sqlite', 'dict']
    query_results = {}
    
    # Define test queries
    test_queries = [
        {
            'name': 'Date Range Query',
            'filters': {'date': {'min': '2023-06-01', 'max': '2023-06-30'}}
        },
        {
            'name': 'Amount Range Query',
            'filters': {'amount': {'min': 500, 'max': 1500}}
        },
        {
            'name': 'Category Filter',
            'filters': {'category': 'Revenue'}
        },
        {
            'name': 'Currency Filter',
            'filters': {'currency': 'USD'}
        },
        {
            'name': 'Complex Query',
            'filters': {
                'category': 'Revenue',
                'amount': {'min': 1000},
                'currency': 'USD'
            }
        }
    ]
    
    for strategy in storage_strategies:
        print(f"\n🔍 Testing {strategy.upper()} query performance...")
        
        # Initialize storage
        storage = DataStorage(storage_type=strategy)
        dataset_id = storage.store_data(df, {'source': 'sample', 'strategy': strategy})
        
        strategy_results = {}
        
        for query in test_queries:
            def run_query():
                return storage.query_by_criteria(query['filters'], dataset_id)
            
            metrics = calculate_performance_metrics(run_query)
            result_df = run_query()
            
            strategy_results[query['name']] = {
                'execution_time': metrics['execution_time_seconds'],
                'result_count': len(result_df),
                'memory_used': metrics['memory_used_mb']
            }
            
            print(f"   {query['name']}: {metrics['execution_time_seconds']:.4f}s ({len(result_df)} results)")
        
        query_results[strategy] = strategy_results
    
    # Compare query performance
    print("\n📊 Query Performance Comparison:")
    print("-" * 60)
    for query_name in test_queries:
        print(f"\n{query_name['name']}:")
        for strategy in storage_strategies:
            result = query_results[strategy][query_name]
            print(f"  {strategy.upper():>10}: {result['execution_time']:>8.4f}s | {result['result_count']:>6} results")
    
    return query_results


def benchmark_aggregation_performance(df: pd.DataFrame):
    """Benchmark aggregation performance."""
    print("\n=== Aggregation Performance Benchmarking ===")
    print("=" * 50)
    
    storage_strategies = ['pandas', 'sqlite', 'dict']
    agg_results = {}
    
    # Define test aggregations
    test_aggregations = [
        {
            'name': 'Sum by Category',
            'group_by': ['category'],
            'measures': ['amount:sum']
        },
        {
            'name': 'Sum by Currency',
            'group_by': ['currency'],
            'measures': ['amount:sum']
        },
        {
            'name': 'Monthly Sum',
            'group_by': ['date'],
            'measures': ['amount:sum']
        },
        {
            'name': 'Complex Aggregation',
            'group_by': ['category', 'currency'],
            'measures': ['amount:sum', 'amount:mean', 'amount:count']
        }
    ]
    
    for strategy in storage_strategies:
        print(f"\n📊 Testing {strategy.upper()} aggregation performance...")
        
        # Initialize storage
        storage = DataStorage(storage_type=strategy)
        dataset_id = storage.store_data(df, {'source': 'sample', 'strategy': strategy})
        
        strategy_results = {}
        
        for agg in test_aggregations:
            def run_aggregation():
                return storage.aggregate_data(agg['group_by'], agg['measures'], dataset_id)
            
            metrics = calculate_performance_metrics(run_aggregation)
            result_df = run_aggregation()
            
            strategy_results[agg['name']] = {
                'execution_time': metrics['execution_time_seconds'],
                'result_count': len(result_df),
                'memory_used': metrics['memory_used_mb']
            }
            
            print(f"   {agg['name']}: {metrics['execution_time_seconds']:.4f}s ({len(result_df)} groups)")
        
        agg_results[strategy] = strategy_results
    
    # Compare aggregation performance
    print("\n📊 Aggregation Performance Comparison:")
    print("-" * 60)
    for agg_name in test_aggregations:
        print(f"\n{agg_name['name']}:")
        for strategy in storage_strategies:
            result = agg_results[strategy][agg_name]
            print(f"  {strategy.upper():>10}: {result['execution_time']:>8.4f}s | {result['result_count']:>6} groups")
    
    return agg_results


def demonstrate_indexing_benefits(df: pd.DataFrame):
    """Demonstrate the benefits of indexing."""
    print("\n=== Indexing Benefits Demonstration ===")
    print("=" * 50)
    
    # Test with pandas storage (which supports indexing)
    storage = DataStorage(storage_type='pandas')
    dataset_id = storage.store_data(df, {'source': 'sample'})
    
    # Define columns to index
    index_columns = ['date', 'amount', 'category', 'currency']
    
    print("Creating indexes...")
    index_info = storage.create_indexes(index_columns, dataset_id)
    
    print(f"✅ Created {len(index_info[dataset_id])} indexes")
    for col, info in index_info[dataset_id].items():
        print(f"   📋 {col}: {info['type']} index")
        if 'unique_values' in info:
            print(f"      Unique values: {len(info['unique_values'])}")
    
    # Test query performance with and without indexes
    test_query = {'category': 'Revenue', 'amount': {'min': 1000}}
    
    print("\n🔍 Testing query performance:")
    
    # Query without indexes (fresh storage)
    fresh_storage = DataStorage(storage_type='pandas')
    fresh_dataset_id = fresh_storage.store_data(df, {'source': 'sample'})
    
    def query_without_index():
        return fresh_storage.query_by_criteria(test_query, fresh_dataset_id)
    
    metrics_no_index = calculate_performance_metrics(query_without_index)
    
    # Query with indexes
    def query_with_index():
        return storage.query_by_criteria(test_query, dataset_id)
    
    metrics_with_index = calculate_performance_metrics(query_with_index)
    
    print(f"   Without indexes: {metrics_no_index['execution_time_seconds']:.4f}s")
    print(f"   With indexes:    {metrics_with_index['execution_time_seconds']:.4f}s")
    
    if metrics_no_index['execution_time_seconds'] > 0:
        improvement = ((metrics_no_index['execution_time_seconds'] - metrics_with_index['execution_time_seconds']) / 
                      metrics_no_index['execution_time_seconds']) * 100
        print(f"   Performance improvement: {improvement:.1f}%")


def demonstrate_data_quality_analysis(df: pd.DataFrame):
    """Demonstrate data quality analysis capabilities."""
    print("\n=== Data Quality Analysis ===")
    print("=" * 40)
    
    from src.utils.validators import validate_financial_data_quality
    
    # Analyze data quality
    quality_report = validate_financial_data_quality(df)
    
    print(f"📊 Overall Quality Score: {quality_report['overall_score']}%")
    print(f"✅ Checks passed: {quality_report['checks_passed']}/{quality_report['total_checks']}")
    
    if quality_report['issues']:
        print("\n⚠️  Issues found:")
        for issue in quality_report['issues']:
            print(f"   • {issue}")
    
    if quality_report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in quality_report['recommendations']:
            print(f"   • {rec}")
    
    # Create detailed summary report
    summary = create_summary_report(df, "Financial Data Quality Analysis")
    
    print(f"\n📈 Data Summary:")
    print(f"   Rows: {summary['basic_info']['rows']:,}")
    print(f"   Columns: {summary['basic_info']['columns']}")
    print(f"   Memory usage: {summary['basic_info']['memory_usage_mb']:.2f} MB")
    print(f"   Null values: {summary['basic_info']['null_values']}")
    print(f"   Duplicate rows: {summary['basic_info']['duplicate_rows']}")


def main():
    """Main function demonstrating performance features."""
    print("=== Financial Data Parser - Performance Demo ===\n")
    
    # Create sample data
    sample_df = create_sample_financial_data(10000)
    
    # Run benchmarks
    storage_results = benchmark_storage_strategies(sample_df)
    query_results = benchmark_query_performance(sample_df)
    agg_results = benchmark_aggregation_performance(sample_df)
    
    # Demonstrate advanced features
    demonstrate_indexing_benefits(sample_df)
    demonstrate_data_quality_analysis(sample_df)
    
    print("\n✅ Performance demo completed!")
    print("\nKey insights:")
    print("- Different storage strategies have varying performance characteristics")
    print("- Indexing can significantly improve query performance")
    print("- Aggregation performance varies by storage type")
    print("- Data quality analysis helps identify issues")
    print("- Memory usage varies significantly between strategies")


if __name__ == "__main__":
    main() 