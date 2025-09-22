"""
Tests for MLON's CLI functionality.
"""
import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
from click.testing import CliRunner

from mlon.cli import cli
from mlon.exceptions import MLONError

class TestCLI(unittest.TestCase):
    """Test suite for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Create sample dataset
        np.random.seed(42)
        n_samples = 100
        
        X = np.random.normal(0, 1, (n_samples, 3))
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        
        self.df = pd.DataFrame(X, columns=['feature_1', 'feature_2', 'feature_3'])
        self.df['target'] = y
        self.df['gender'] = np.random.choice(['M', 'F'], size=n_samples)
        
    def test_basic_check(self):
        """Test basic CLI check command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save test data
            data_path = Path(tmpdir) / 'data.csv'
            self.df.to_csv(data_path, index=False)
            
            # Run CLI command
            result = self.runner.invoke(cli, ['check', str(data_path)])
            
            # Check success
            self.assertEqual(result.exit_code, 0)
            
            # Check output contains key sections
            self.assertIn('Data Overview', result.output)
            self.assertIn('Data Leakage', result.output)
            self.assertIn('Bias Detection', result.output)
            
    def test_check_with_options(self):
        """Test CLI check command with various options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save test data
            data_path = Path(tmpdir) / 'data.csv'
            train_path = Path(tmpdir) / 'train.csv'
            test_path = Path(tmpdir) / 'test.csv'
            output_path = Path(tmpdir) / 'report.pdf'
            
            self.df.to_csv(data_path, index=False)
            self.df.iloc[:80].to_csv(train_path, index=False)
            self.df.iloc[60:].to_csv(test_path, index=False)
            
            # Run CLI command with all options
            result = self.runner.invoke(cli, [
                'check',
                str(data_path),
                '--train-data', str(train_path),
                '--test-data', str(test_path),
                '--target', 'target',
                '--protected', 'gender',
                '--output', str(output_path),
                '--verbose'
            ])
            
            # Check success
            self.assertEqual(result.exit_code, 0)
            
            # Verify PDF was created
            self.assertTrue(output_path.exists())
            
    def test_error_handling(self):
        """Test CLI error handling."""
        # Test with non-existent file
        result = self.runner.invoke(cli, ['check', 'nonexistent.csv'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Error', result.output)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with invalid CSV
            invalid_path = Path(tmpdir) / 'invalid.csv'
            invalid_path.write_text('invalid,csv,file\n1,2,')
            
            result = self.runner.invoke(cli, ['check', str(invalid_path)])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Error', result.output)
            
    def test_logging(self):
        """Test CLI logging functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / 'data.csv'
            self.df.to_csv(data_path, index=False)
            
            # Test with verbose logging
            with patch('mlon.cli.setup_cli_logging') as mock_logging:
                result = self.runner.invoke(cli, [
                    'check',
                    str(data_path),
                    '--verbose'
                ])
                
                # Verify logging was configured correctly
                mock_logging.assert_called_once_with(True)
                
    def test_output_formats(self):
        """Test different output formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir) / 'data.csv'
            self.df.to_csv(data_path, index=False)
            
            # Test PDF output
            pdf_path = Path(tmpdir) / 'report.pdf'
            result = self.runner.invoke(cli, [
                'check',
                str(data_path),
                '--output', str(pdf_path)
            ])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(pdf_path.exists())

if __name__ == '__main__':
    unittest.main()
