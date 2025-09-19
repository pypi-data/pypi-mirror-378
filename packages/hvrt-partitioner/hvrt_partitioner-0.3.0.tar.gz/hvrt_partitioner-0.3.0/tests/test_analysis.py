
import pandas as pd
import numpy as np
import os
import shutil

# Assuming tests are run from the project root and the package is installed in editable mode
from src.hvrt import HVRTPartitioner, DistributionAnalyzer

def test_analyzer_output_generation_for_manual_review():
    """
    Tests that the DistributionAnalyzer correctly creates an output plot for each feature.
    This test saves artifacts to a permanent directory for manual inspection.
    """
    # 1. Define a permanent output directory
    output_dir = "test_outputs/analyzer_output"

    # 2. Ensure a clean state before the test
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # 3. Create synthetic data
    data_size = 1000
    features = {
        f'feature_{chr(65 + i)}': np.random.randn(data_size) * (i + 1)
        for i in range(3)
    }
    X = pd.DataFrame(features)

    # 4. Create partitions
    partitioner = HVRTPartitioner(max_leaf_nodes=10)
    partitioner.fit(X)
    labels = partitioner.get_partitions(X)

    # 5. Run the DistributionAnalyzer
    analyzer = DistributionAnalyzer(
        data=X, 
        partition_labels=pd.Series(labels, index=X.index)
    )
    analyzer.fit()

    # 6. Generate plots and assert creation for each feature
    print(f"\nSaving analysis plots to: {os.path.abspath(output_dir)}")
    for feature in X.columns:
        feature_path = os.path.join(output_dir, feature)
        os.makedirs(feature_path, exist_ok=True)
        
        plot_path = os.path.join(feature_path, "distribution_comparison.png")
        
        analyzer.plot_comparison(feature, save_path=plot_path)
        
        assert os.path.isfile(plot_path), f"Plot for feature '{feature}' was not created."

    print("\nAssertions passed. Artifacts are available for manual review.")
