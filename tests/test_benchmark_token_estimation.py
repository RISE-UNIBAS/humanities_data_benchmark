#!/usr/bin/env python3
"""Unit tests for token estimation methods in benchmark_base.py"""

import sys
import os
# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

import unittest
import tempfile
import json
from unittest.mock import patch, Mock, mock_open, MagicMock
from benchmark_base import Benchmark


class MockBenchmark(Benchmark):
    """Mock implementation of Benchmark for testing."""

    def __init__(self, *args, **kwargs):
        # Initialize with minimal required attributes
        self.benchmark_dir = "/test/benchmark"
        self.has_file_information = True

    def score_benchmark(self, all_scores):
        return {"score": 1.0}

    def score_request_answer(self, image_name, response, ground_truth):
        return {"score": 1.0}

    def create_request_render(self, image_name, result, score, truth):
        return "mock render"

    def load_prompt(self):
        return "This is a test prompt for token estimation with some content to count."

    def get_file_path(self, image_name):
        return f"/test/images/{image_name}.jpg"


class TestBenchmarkTokenEstimation(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.benchmark = MockBenchmark()

    def test_estimate_input_tokens_text_only(self):
        """Test input token estimation for text-only benchmark."""
        self.benchmark.has_file_information = False

        tokens = self.benchmark.estimate_input_tokens("test_image")

        # Should only count text tokens (prompt length // 5)
        prompt = self.benchmark.load_prompt()
        expected_tokens = len(prompt) // 5
        self.assertEqual(tokens, expected_tokens)

    @patch('data_loader.resize_image')
    @patch('tempfile.TemporaryDirectory')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    @patch('base64.b64encode')
    @patch('os.path.exists')
    def test_estimate_input_tokens_with_image(self, mock_exists, mock_b64encode, mock_file,
                                            mock_temp_dir, mock_resize):
        """Test input token estimation with image."""
        mock_exists.return_value = True
        mock_temp_dir.return_value.__enter__.return_value = "/tmp/test"
        mock_resize.return_value = "/tmp/test/resized.jpg"
        mock_b64encode.return_value.decode.return_value = "base64_encoded_image_data"

        tokens = self.benchmark.estimate_input_tokens("test_image")

        # Should include both text and image tokens
        prompt = self.benchmark.load_prompt()
        expected_text_tokens = len(prompt) // 5
        expected_image_tokens = 2000
        expected_total = expected_text_tokens + expected_image_tokens

        self.assertEqual(tokens, expected_total)

    @patch('os.path.exists')
    def test_estimate_input_tokens_image_not_found(self, mock_exists):
        """Test input token estimation when image file doesn't exist."""
        mock_exists.return_value = False

        tokens = self.benchmark.estimate_input_tokens("nonexistent_image")

        # Should use fallback image tokens
        prompt = self.benchmark.load_prompt()
        expected_text_tokens = len(prompt) // 5
        expected_image_tokens = 2000  # Fallback
        expected_total = expected_text_tokens + expected_image_tokens

        self.assertEqual(tokens, expected_total)

    def test_estimate_output_tokens_dict_response(self):
        """Test output token estimation from dictionary response."""
        answer = {
            'response_text': {
                'title': 'Test Document',
                'entries': [
                    {'id': 1, 'text': 'Some content'},
                    {'id': 2, 'text': 'More content here'}
                ]
            }
        }

        tokens = self.benchmark.estimate_output_tokens(answer)

        # Should convert dict to JSON string and count characters
        json_str = json.dumps(answer['response_text'])
        expected_tokens = max(len(json_str) // 4, 1)

        self.assertEqual(tokens, expected_tokens)

    def test_estimate_output_tokens_string_response(self):
        """Test output token estimation from string response."""
        answer = {
            'response_text': 'This is a simple string response for testing token estimation.'
        }

        tokens = self.benchmark.estimate_output_tokens(answer)

        expected_tokens = max(len(answer['response_text']) // 4, 1)
        self.assertEqual(tokens, expected_tokens)

    def test_estimate_output_tokens_empty_response(self):
        """Test output token estimation with empty response."""
        answer = {'response_text': ''}

        tokens = self.benchmark.estimate_output_tokens(answer)

        # Should return at least 1 token
        self.assertEqual(tokens, 1)

    def test_estimate_output_tokens_no_response_text(self):
        """Test output token estimation with missing response_text."""
        answer = {'other_field': 'value'}

        tokens = self.benchmark.estimate_output_tokens(answer)

        # Should handle missing response_text gracefully
        self.assertEqual(tokens, 1)

    @patch('benchmark_base.logging')
    def test_estimate_input_tokens_error_handling(self, mock_logging):
        """Test error handling in input token estimation."""
        # Mock load_prompt to raise an exception
        with patch.object(self.benchmark, 'load_prompt', side_effect=Exception("Test error")):
            tokens = self.benchmark.estimate_input_tokens("test_image")

        # Should return fallback value
        self.assertEqual(tokens, 1000)
        mock_logging.warning.assert_called()

    @patch('benchmark_base.logging')
    def test_estimate_output_tokens_error_handling(self, mock_logging):
        """Test error handling in output token estimation."""
        # Create an answer that will cause JSON serialization to fail
        answer = {'response_text': {'circular': None}}
        answer['response_text']['circular'] = answer['response_text']  # Circular reference

        tokens = self.benchmark.estimate_output_tokens(answer)

        # Should return fallback value
        self.assertEqual(tokens, 100)
        mock_logging.warning.assert_called()

    def test_token_estimation_consistency(self):
        """Test that token estimation is consistent across calls."""
        answer = {'response_text': 'Consistent test content for token counting.'}

        tokens1 = self.benchmark.estimate_output_tokens(answer)
        tokens2 = self.benchmark.estimate_output_tokens(answer)

        self.assertEqual(tokens1, tokens2)

    @patch('os.path.exists')
    def test_estimate_input_tokens_various_prompt_sizes(self, mock_exists):
        """Test token estimation with different prompt sizes."""
        mock_exists.return_value = False  # Skip image processing
        self.benchmark.has_file_information = False

        # Test with different prompt lengths
        short_prompt = "Short"
        long_prompt = "A" * 1000

        with patch.object(self.benchmark, 'load_prompt', return_value=short_prompt):
            short_tokens = self.benchmark.estimate_input_tokens("test")

        with patch.object(self.benchmark, 'load_prompt', return_value=long_prompt):
            long_tokens = self.benchmark.estimate_input_tokens("test")

        # Longer prompt should result in more tokens
        self.assertGreater(long_tokens, short_tokens)

    def test_estimate_output_tokens_various_response_sizes(self):
        """Test output token estimation with different response sizes."""
        short_answer = {'response_text': 'Short'}
        long_answer = {'response_text': 'A' * 1000}

        short_tokens = self.benchmark.estimate_output_tokens(short_answer)
        long_tokens = self.benchmark.estimate_output_tokens(long_answer)

        # Longer response should result in more tokens
        self.assertGreater(long_tokens, short_tokens)


if __name__ == '__main__':
    unittest.main()