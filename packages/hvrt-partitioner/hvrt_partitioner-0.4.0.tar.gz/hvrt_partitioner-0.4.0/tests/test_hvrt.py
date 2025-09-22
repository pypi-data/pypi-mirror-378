import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
from src.hvrt.partitioner import HVRTPartitioner
from src.metrics.metrics import full_report
from src.metrics.partition_profiler import PartitionProfiler

def test_partitioning():
    """
    Tests that the HVRTPartitioner creates the correct number of partitions.
    """
    # Create a sample dataset
    X = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100)
    })

    # Create a partitioner
    partitioner = HVRTPartitioner(max_leaf_nodes=10)

    # Fit the partitioner and get the partitions
    partitions = partitioner.fit_predict(X)

    # Check that the number of unique partitions is less than or equal to the max_leaf_nodes
    assert len(np.unique(partitions)) <= 10

def test_partitioner_multi_output():
    """
    Tests that the HVRTPartitioner works correctly with a multi-output target.
    """
    # Create a sample dataset with continuous and categorical features
    X = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })

    # Create a partitioner
    partitioner = HVRTPartitioner(max_leaf_nodes=10)

    # Fit the partitioner and get the partitions
    partitions = partitioner.fit_predict(X)

    # Check that the number of unique partitions is less than or equal to the max_leaf_nodes
    assert len(np.unique(partitions)) <= 10

def test_metrics_report():
    """
    Tests that the full_report function generates a report without errors.
    """
    # Create a sample dataset
    X = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100)
    })

    # Create a partitioner
    partitioner = HVRTPartitioner(max_leaf_nodes=10, min_variance_reduction=0.0)

    # Fit the partitioner and get the partitions
    partitions = partitioner.fit_predict(X)

    # Generate the full report
    report = full_report(X, partitions)

    # Check that the report is a dictionary and is not empty
    assert isinstance(report, dict)
    assert len(report) > 0

def test_metrics_full_report():
    """
    Tests the full_report function in more detail.
    """
    # Create a sample dataset
    X = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100)
    })

    # Create a partitioner
    partitioner = HVRTPartitioner(max_leaf_nodes=10, min_variance_reduction=0.0)

    # Fit the partitioner and get the partitions
    partitions = partitioner.fit_predict(X)

    # Generate the full report
    report = full_report(X, partitions)

    # Check that the report has the correct structure
    assert isinstance(report, dict)
    for feature_name, feature_report in report.items():
        assert feature_name in X.columns
        assert hasattr(feature_report, 'variance_report')
        assert hasattr(feature_report, 'span_report')

def test_partition_profiler():
    """
    Tests the PartitionProfiler class.
    """
    # Create a sample dataset
    X = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100)
    })

    # Create a partitioner
    partitioner = HVRTPartitioner(max_leaf_nodes=10, min_variance_reduction=0.0)

    # Fit the partitioner and get the partitions
    partitions = partitioner.fit_predict(X)

    # Create a PartitionProfiler
    profiler = PartitionProfiler(X, pd.Series(partitions))

    # Run the profiling
    profiler.run_profiling()

    # Check that the summary table is generated
    summary_table = profiler.generate_summary_table()
    assert isinstance(summary_table, pd.DataFrame)
    assert not summary_table.empty
