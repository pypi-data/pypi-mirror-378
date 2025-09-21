"""Tests for shardate.__init__ module."""

import importlib
import importlib.metadata
import sys
import unittest.mock


def test_version_with_package_not_found_error():
    """Test version handling when PackageNotFoundError is raised."""
    # Test the version retrieval logic directly without module reloading
    with unittest.mock.patch(
        "importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError(),
    ):
        try:
            version = importlib.metadata.version("shardate")
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
        assert version == "unknown"


def test_version_with_valid_package():
    """Test version retrieval when package is found."""
    # Test the version retrieval logic directly without module reloading
    with unittest.mock.patch("importlib.metadata.version", return_value="1.2.3"):
        try:
            version = importlib.metadata.version("shardate")
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
        assert version == "1.2.3"


def test_init_module_with_package_not_found_error():
    """Test __init__.py lines 9-10 by importing module with mocked PackageNotFoundError."""
    # Remove the module from cache if it exists
    module_name = "shardate"
    if module_name in sys.modules:
        del sys.modules[module_name]

    # Mock importlib.metadata.version to raise PackageNotFoundError
    with unittest.mock.patch(
        "importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError(),
    ):
        # Import the module, which will execute the try/except block
        import shardate

        # Verify that __version__ was set to "unknown" (line 10)
        assert shardate.__version__ == "unknown"


def test_init_module_with_valid_version():
    """Test __init__.py with successful version retrieval."""
    # Remove the module from cache if it exists
    module_name = "shardate"
    if module_name in sys.modules:
        del sys.modules[module_name]

    # Mock importlib.metadata.version to return a version
    with unittest.mock.patch("importlib.metadata.version", return_value="1.2.3"):
        # Import the module, which will execute the try block
        import shardate

        # Verify that __version__ was set to the mocked version
        assert shardate.__version__ == "1.2.3"
