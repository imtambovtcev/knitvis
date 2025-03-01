import pytest
import numpy as np
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from knitvis import KnittingChart
from knitvis.gui.views import ChartView
from knitvis.gui.controllers import ChartController

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
def chart_view(sample_chart):
    """Create a ChartView with the sample chart"""
    view = ChartView(sample_chart)
    controller = ChartController(view, sample_chart)
    return view


def test_chart_view_initialization(chart_view):
    """Test that the ChartView initializes correctly with a chart"""
    # Check that the chart view is created
    assert chart_view is not None

    # Check that the figure and canvas are created
    assert chart_view.figure is not None
    assert chart_view.canvas is not None

    # Check that the layout contains the canvas
    # Use itemAt to check if canvas is in the layout
    found = False
    for i in range(chart_view.layout.count()):
        if chart_view.layout.itemAt(i).widget() == chart_view.canvas:
            found = True
            break
    assert found, "Canvas not found in layout"


def test_chart_view_update(chart_view, sample_chart):
    """Test that the view updates when the chart changes"""
    # Get original figure
    original_figure = chart_view.figure

    # Modify the chart and update view
    sample_chart.set_stitch(0, 0, stitch_type='P')
    chart_view.update_view()

    # Figure should still be the same object (reused)
    assert chart_view.figure is original_figure


def test_chart_view_click_signal(qtbot, chart_view):
    """Test that clicking on the chart emits the stitch_clicked signal"""
    # Create signal spy
    with qtbot.waitSignal(chart_view.stitch_clicked, timeout=100) as spy:
        # Calculate center of chart cell at position (1, 1)
        # In the chart view, the origin is bottom-left, but click is top-down
        # For a 5x5 chart, clicking at position (1, 1) means:
        # x = 1.5 (between 1 and 2) in chart coordinates
        # y = 3.5 (between 3 and 4) in chart coordinates (since row 1 is the 4th row from the bottom)

        # Trigger the click signal directly since we can't click on the matplotlib canvas directly
        # in a test environment
        event = type('obj', (object,), {
            'xdata': 1.5,
            'ydata': 3.5,
        })
        chart_view.on_canvas_click(event)

    # First signal argument should be row=1
    assert spy.args[0] == 1
    # Second signal argument should be col=1
    assert spy.args[1] == 1
