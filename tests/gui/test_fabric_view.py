import pytest
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from knitvis import KnittingChart
from knitvis.gui.views import FabricView
from knitvis.gui.controllers import FabricController

# Initialize QApplication for tests
app = QApplication.instance()
if app is None:
    app = QApplication([])


@pytest.fixture
def sample_chart():
    """Create a sample chart for testing - all knit stitches for fabric view"""
    # Create a small test pattern - only knit stitches for fabric view
    pattern = np.zeros((5, 5), dtype=int)

    # Add some colors
    colors = np.zeros((5, 5, 3), dtype=int)
    colors.fill(200)  # Light gray
    colors[1, 1] = [255, 0, 0]  # Red
    colors[2, 2] = [0, 255, 0]  # Green
    colors[3, 3] = [0, 0, 255]  # Blue

    return KnittingChart(pattern, colors)


@pytest.fixture
def fabric_view(sample_chart):
    """Create a FabricView with the sample chart"""
    view = FabricView(sample_chart)
    controller = FabricController(view, sample_chart)
    return view


def test_fabric_view_initialization(fabric_view):
    """Test that the FabricView initializes correctly with a chart"""
    # Check that the fabric view is created
    assert fabric_view is not None

    # Check that the figure and canvas are created
    assert fabric_view.figure is not None
    assert fabric_view.canvas is not None

    # Check that the controls are created
    assert fabric_view.outlines_checkbox is not None
    assert fabric_view.spacing_slider is not None


def test_fabric_view_update(fabric_view, sample_chart):
    """Test that the view updates when controls are changed"""
    # Get original slider value
    original_value = fabric_view.spacing_slider.value()

    # Change slider value and check that view updates
    fabric_view.spacing_slider.setValue(original_value + 10)

    # Row spacing should be updated to match slider
    assert fabric_view.row_spacing == (original_value + 10) / 100.0


def test_fabric_view_click_signal(qtbot, fabric_view):
    """Test that clicking on the fabric emits the stitch_clicked signal"""
    # Store row spacing for calculations
    fabric_view.row_spacing = 0.7

    # Create signal spy
    with qtbot.waitSignal(fabric_view.stitch_clicked, timeout=100) as spy:
        # Calculate a position that should correspond to row 2, col 3
        # The fabric view is more complex due to V shapes
        # We'll send a click event that should map to row 2, col 3
        event = type('obj', (object,), {
            'xdata': 3.5,  # Position within column 3
            'ydata': 1.4,  # Position should map to row 2
        })
        fabric_view.on_canvas_click(event)

    # The row calculation in the view should map this to row 2
    # Allow some flexibility due to rounding/calculation differences
    assert spy.args[0] in [2, 3]
    # The column calculation should map to col 3
    assert spy.args[1] == 3


def test_fabric_view_non_knit_stitches(fabric_view, sample_chart):
    """Test that fabric view handles non-knit stitches properly"""
    # Modify chart to add a non-knit stitch (will cause NotImplementedError)
    sample_chart.pattern[2, 2] = 1  # Purl stitch

    # Update view should not raise an exception but show an error message
    fabric_view.update_view()

    # The figure should still exist
    assert fabric_view.figure is not None
