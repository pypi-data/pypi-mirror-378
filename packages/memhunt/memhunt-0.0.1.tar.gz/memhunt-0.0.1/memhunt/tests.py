"""
Modern test suite for memhunt

This replaces the old Plone-based tests with modern pytest-based tests.
For the actual test implementations, see the tests/ directory.
"""
import pytest


def test_suite():
    """
    Compatibility function for old test runners.
    Modern testing should use pytest directly.
    """
    # Run pytest programmatically if needed
    return pytest.main(['-v', 'tests/'])


if __name__ == '__main__':
    # Run the tests using pytest
    pytest.main(['-v', 'tests/', '--cov=objgraph'])

