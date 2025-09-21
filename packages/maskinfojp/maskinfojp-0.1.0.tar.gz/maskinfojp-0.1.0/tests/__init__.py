"""
Test suite initialization
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import maskinfo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .test_detector import TestSensitiveDetector
from .test_masker import TestSensitiveMasker
from .test_file_handler import TestFileHandler, TestTextFileHandler, TestBinaryFileHandler


def create_test_suite():
    """Create a comprehensive test suite."""
    test_suite = unittest.TestSuite()
    
    # Add detector tests
    test_suite.addTest(unittest.makeSuite(TestSensitiveDetector))
    
    # Add masker tests
    test_suite.addTest(unittest.makeSuite(TestSensitiveMasker))
    
    # Add file handler tests
    test_suite.addTest(unittest.makeSuite(TestFileHandler))
    test_suite.addTest(unittest.makeSuite(TestTextFileHandler))
    test_suite.addTest(unittest.makeSuite(TestBinaryFileHandler))
    
    return test_suite


def run_all_tests():
    """Run all tests."""
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    run_all_tests()