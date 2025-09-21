#!/usr/bin/env python3
"""
Example usage of finlab-guard package.

This demonstrates the basic functionality without requiring actual finlab package.
"""

import pandas as pd
from datetime import datetime
from finlab_guard import FinlabGuard

def main():
    """Main example function."""
    print("=== finlab-guard Example ===\n")

    # Create FinlabGuard instance
    guard = FinlabGuard(cache_dir="./example_cache")
    print(f"✓ FinlabGuard initialized with cache_dir: {guard.cache_dir}")

    # Create sample data (simulating finlab data)
    sample_data = pd.DataFrame({
        '2023-01-01': [100, 200, 300],
        '2023-01-02': [101, 199, 305],
        '2023-01-03': [102, 201, 298]
    }, index=['AAPL', 'GOOGL', 'TSLA'])
    sample_data.index.name = 'symbol'
    sample_data.columns.name = 'date'

    print("\n--- Sample Data ---")
    print(sample_data)

    # Manually save data (simulating first finlab fetch)
    timestamp1 = datetime(2023, 1, 1, 10, 0, 0)
    guard.cache_manager.save_data('price:close', sample_data, timestamp1)
    print(f"\n✓ Saved data at {timestamp1}")

    # Load the data back
    loaded_data = guard.cache_manager.load_data('price:close')
    print("\n--- Loaded Data ---")
    print(loaded_data)

    # Verify data integrity
    try:
        pd.testing.assert_frame_equal(sample_data, loaded_data)
        print("✓ Data integrity verified")
    except AssertionError:
        print("✗ Data integrity check failed")

    # Test time-based queries
    print(f"\n--- Time Context Demo ---")

    # Add more data at a later time
    modified_data = sample_data.copy()
    modified_data.loc['AAPL', '2023-01-01'] = 999  # Simulate data change

    timestamp2 = datetime(2023, 1, 1, 11, 0, 0)
    guard.cache_manager.save_data('price:close', modified_data, timestamp2)
    print(f"✓ Saved modified data at {timestamp2}")

    # Query data at different times
    data_at_t1 = guard.cache_manager.load_data('price:close', timestamp1)
    data_at_t2 = guard.cache_manager.load_data('price:close', timestamp2)

    print(f"\nData at {timestamp1}:")
    print(f"AAPL price: {data_at_t1.loc['AAPL', '2023-01-01']}")

    print(f"\nData at {timestamp2}:")
    print(f"AAPL price: {data_at_t2.loc['AAPL', '2023-01-01']}")

    # Test change detection
    print(f"\n--- Change Detection Demo ---")

    validator = guard.validator
    modifications, additions = validator.detect_changes_detailed(
        'price:close', modified_data, guard.cache_manager
    )

    print(f"Detected {len(modifications)} modifications:")
    for change in modifications:
        print(f"  {change}")

    # Storage info
    print(f"\n--- Storage Info ---")
    storage_info = guard.cache_manager.get_storage_info()
    for key, info in storage_info.items():
        if key != 'total_size':
            print(f"Dataset '{key}': {info['file_size']} bytes, {info.get('record_count', 'N/A')} records")

    print(f"Total storage: {storage_info.get('total_size', 0)} bytes")

    print(f"\n✓ Example completed successfully!")

if __name__ == '__main__':
    import finlab
    from finlab import data
    guard = FinlabGuard()
    guard.install_patch()
    data.get('price:收盤價')
    finlab.data.get('price:收盤價')
    main()