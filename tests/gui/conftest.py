"""Common test fixtures for GUI tests."""
import pytest
from PyQt5.QtWidgets import QApplication

# Important: Define this here so it's available for all tests


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
