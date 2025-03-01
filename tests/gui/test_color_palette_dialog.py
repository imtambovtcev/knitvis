import pytest
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QWidget
from PyQt5.QtGui import QColor

from knitvis import KnittingChart
from knitvis.gui.dialogs import ColorPaletteDialog

# Initialize QApplication for tests
app = QApplication.instance()
if app is None:
    app = QApplication([])


class MockMainWindow(QWidget):
    """Mock main window class for testing the dialog"""

    def __init__(self, chart):
        super().__init__()
        self.chart = chart
        self.controllers = []


@pytest.fixture
def sample_chart():
    """Create a sample chart with multiple colors for testing"""
    # Create a small test pattern
    pattern = np.zeros((5, 5), dtype=int)

    # Add different colors to create a palette
    colors = np.zeros((5, 5, 3), dtype=int)
    colors[0:2, 0:2] = [255, 0, 0]    # Red
    colors[0:2, 2:4] = [0, 255, 0]    # Green
    colors[2:4, 0:2] = [0, 0, 255]    # Blue
    colors[2:4, 2:4] = [255, 255, 0]  # Yellow

    return KnittingChart(pattern, colors)


@pytest.fixture
def color_palette_dialog(qtbot, sample_chart):
    """Create a ColorPaletteDialog for testing"""
    parent = MockMainWindow(sample_chart)
    dialog = ColorPaletteDialog(parent)
    qtbot.addWidget(dialog)
    return dialog


def test_color_palette_dialog_initialization(color_palette_dialog, sample_chart):
    """Test that the dialog initializes correctly with the chart's palette"""
    # Check that the color list is populated with the chart's colors
    assert color_palette_dialog.color_list.count(
    ) == sample_chart.color_palette.num_colors

    # Check that the palette preview is created
    assert color_palette_dialog.figure is not None
    assert color_palette_dialog.canvas is not None


def test_color_selection(qtbot, color_palette_dialog):
    """Test selecting a color in the list"""
    # Initially no color is selected, button should be disabled
    assert not color_palette_dialog.edit_color_button.isEnabled()

    # Select the first color
    color_palette_dialog.color_list.setCurrentRow(0)

    # Button should be enabled
    assert color_palette_dialog.edit_color_button.isEnabled()


def test_apply_settings(qtbot, color_palette_dialog, sample_chart):
    """Test applying color changes"""
    # Mock to track if chart is updated
    calls = []

    # Override apply_settings method to record calls
    original_apply = color_palette_dialog.apply_settings

    def mock_apply():
        calls.append(1)
        original_apply()
    color_palette_dialog.apply_settings = mock_apply

    # Create a modified color and add it to the dialog's modified_colors
    new_color = (100, 150, 200)
    color_palette_dialog.modified_colors[0] = new_color

    # Call accept which should call apply_settings
    color_palette_dialog.accept()

    # Check that apply_settings was called
    assert len(calls) == 1
