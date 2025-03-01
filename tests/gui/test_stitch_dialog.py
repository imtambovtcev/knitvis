import pytest
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QColor

from knitvis import KnittingChart
from knitvis.gui.dialogs import StitchDialog

# Initialize QApplication for tests
app = QApplication.instance()
if app is None:
    app = QApplication([])


@pytest.fixture
def sample_chart():
    """Create a sample chart for testing"""
    # Create a small test pattern
    pattern = np.zeros((5, 5), dtype=int)

    # Add some different stitch types
    pattern[1, 1] = 1  # Purl
    pattern[2, 2] = 2  # YO
    pattern[3, 3] = 3  # K2tog

    # Add some colors
    colors = np.zeros((5, 5, 3), dtype=int)
    colors.fill(200)  # Light gray
    colors[1, 1] = [255, 0, 0]  # Red
    colors[2, 2] = [0, 255, 0]  # Green
    colors[3, 3] = [0, 0, 255]  # Blue

    return KnittingChart(pattern, colors)


@pytest.fixture
def stitch_dialog(qtbot, sample_chart):
    """Create a StitchDialog for testing"""
    dialog = StitchDialog(None, sample_chart, 1,
                          1)  # Position has a purl stitch
    qtbot.addWidget(dialog)
    return dialog


def test_stitch_dialog_initialization(stitch_dialog):
    """Test that the dialog initializes with the correct stitch and color"""
    # Dialog should initialize with values from the chart
    assert stitch_dialog.stitch_combo.currentIndex() == 1  # Purl stitch
    assert stitch_dialog.color_button.color.getRgb()[:3] == (255, 0, 0)  # Red


def test_stitch_dialog_combo_change(qtbot, stitch_dialog):
    """Test changing the stitch type combobox"""
    # Change stitch type to YO (index 2)
    stitch_dialog.stitch_combo.setCurrentIndex(2)

    # Preview should update
    qtbot.wait(50)  # Allow for any update processing

    # Verify stitch_combo index
    assert stitch_dialog.stitch_combo.currentIndex() == 2


def test_stitch_dialog_get_selection(stitch_dialog):
    """Test that get_selection returns the correct values"""
    # Set specific values for testing
    stitch_dialog.stitch_combo.setCurrentIndex(3)  # K2tog
    test_color = QColor(100, 150, 200)
    stitch_dialog.color_button.set_color(test_color)

    # Get the selection
    stitch_index, color = stitch_dialog.get_selection()

    # Check that the values match what was set
    assert stitch_index == 3
    assert color.getRgb()[:3] == (100, 150, 200)
