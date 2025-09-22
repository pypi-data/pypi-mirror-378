"""
Tests for MLON's auto-check functionality.
"""
import unittest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from mlon.auto_check import AutoChecker
from mlon.exceptions import MLONDataError, MLONValueError

class TestAutoChecker(unittest.TestCase):
    """Test suite for AutoChecker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = AutoChecker()
        
        # Create sample dataset
        np.random.seed(42)
        n_samples = 1000
        
        # Features
        X = np.random.normal(0, 1, (n_samples, 5))
        
        # Target (binary classification)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        
        # Create DataFrame
        self.df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)])
        self.df['target'] = y
        
        # Add protected attributes
        self.df['gender'] = np.random.choice(['M', 'F'], size=n_samples, p=[0.7, 0.3])
        self.df['age_group'] = np.random.choice(['<30', '30-50', '>50'], size=n_samples)
        
        # Add leaky feature
        self.df['leaky'] = y + np.random.normal(0, 0.1, size=n_samples)
        
        # Create time series version
        dates = pd.date_range('2025-01-01', periods=n_samples, freq='D')
        self.ts_df = self.df.copy()
        self.ts_df.index = dates
        
    def test_infer_data_type(self):
        """Test data type inference."""
        # Test tabular data
        self.assertEqual(
            self.checker.infer_data_type(self.df),
            'tabular'
        )
        
        # Test time series data
        self.assertEqual(
            self.checker.infer_data_type(self.ts_df),
            'time_series'
        )
        
    def test_infer_target(self):
        """Test target column inference."""
        # Test with explicit target column
        target_col, problem_type = self.checker.infer_target(self.df)
        self.assertEqual(target_col, 'target')
        self.assertEqual(problem_type, 'classification')
        
        # Test with unnamed target
        df = self.df.copy()
        df.columns = [f'feature_{i}' for i in range(len(df.columns))]
        target_col, problem_type = self.checker.infer_target(df)
        self.assertEqual(target_col, df.columns[-1])
        
    def test_infer_protected_features(self):
        """Test protected feature inference."""
        protected_features = self.checker.infer_protected_features(self.df)
        self.assertIn('gender', protected_features)
        self.assertIn('age_group', protected_features)
        
    def test_check_data_basic(self):
        """Test basic data checking functionality."""
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            results = self.checker.check_data(
                self.df,
                output_path=tmp.name
            )
            
            # Check that results contain all expected sections
            self.assertIn('data_overview', results)
            self.assertIn('leakage_detection', results)
            self.assertIn('bias_detection', results)
            self.assertIn('recommendations', results)
            
            # Check that leakage was detected
            leakage_warnings = results['leakage_detection']['target_leakage']
            self.assertTrue(any('leaky' in str(w) for w in leakage_warnings))
            
            # Check that bias was detected
            bias_warnings = results['bias_detection']
            self.assertTrue(any('gender' in str(w) for w in bias_warnings))
            
    def test_check_data_time_series(self):
        """Test time series specific checks."""
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            results = self.checker.check_data(
                self.ts_df,
                output_path=tmp.name
            )
            
            # Verify time series detection
            self.assertEqual(
                results['data_overview']['data_type'],
                'time_series'
            )
            
            # Check for future leakage detection
            self.assertIn('future_leakage', results['leakage_detection'])
            
    def test_check_data_with_splits(self):
        """Test checking with train/test splits."""
        train_df = self.df.iloc[:800]
        test_df = self.df.iloc[750:]  # Deliberate overlap
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            results = self.checker.check_data(
                self.df,
                train_data=train_df,
                test_data=test_df,
                output_path=tmp.name
            )
            
            # Check that overlap was detected
            overlap_warnings = results['leakage_detection']['train_test_overlap']
            self.assertTrue(any('overlap' in str(w) for w in overlap_warnings))
            
    def test_error_handling(self):
        """Test error handling."""
        # Test with invalid DataFrame
        with self.assertRaises(MLONDataError):
            self.checker.check_data(None)
            
        # Test with non-numeric target
        df_invalid = self.df.copy()
        df_invalid['target'] = 'invalid'
        with self.assertRaises(MLONValueError):
            self.checker.check_data(df_invalid)
            
    def test_pdf_generation(self):
        """Test PDF report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'report.pdf'
            results = self.checker.check_data(
                self.df,
                output_path=str(output_path)
            )
            
            # Verify PDF was created
            self.assertTrue(output_path.exists())
            self.assertTrue(output_path.stat().st_size > 0)

if __name__ == '__main__':
    unittest.main()
