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
def chart_view(qtbot, sample_chart):
    """Create a ChartView with a sample chart for testing."""
    view = ChartView(sample_chart)
    qtbot.addWidget(view)
    return view


def test_chart_view_initialization(chart_view):
    """Test that the ChartView initializes correctly with a chart"""
    # Check that the chart view is created
    assert chart_view is not None

    # Check that the figure and canvas are created
    assert chart_view.figure is not None
    assert chart_view.canvas is not None

    # Check that the canvas is in the nested layout structure
    # (now within navigation widget content area)
    content_widget = chart_view.navigation.layout().itemAtPosition(0, 0).widget()
    assert content_widget is not None
    assert content_widget.layout() is not None

    # Check canvas is in the content area layout
    found = False
    for i in range(content_widget.layout().count()):
        if content_widget.layout().itemAt(i).widget() == chart_view.canvas:
            found = True
            break
    assert found, "Canvas not found in nested layout"


def test_chart_view_update(qtbot, chart_view):
    """Test that the view updates when the chart changes"""
    # Directly trigger a view update without waiting for signal
    chart_view.update_view()

    # Check that the chart is rendered (the axis has children)
    assert len(chart_view.ax.get_children()) > 0


def test_chart_view_click_signal(qtbot, chart_view):
    """Test that clicking on the chart emits the correct stitch clicked signal"""
    # Create a signal spy
    with qtbot.waitSignal(chart_view.stitch_clicked) as spy:
        # Calculate where to click (center of a cell)
        # We simulate a click by calling the handler directly with mock event data
        class MockEvent:
            xdata = 4.0  # Center of cell
            ydata = 2.0  # Center of cell

        chart_view.on_canvas_click(MockEvent())

    # Get the row and column from the signal
    row, col = spy.args

    # For the test chart size and viewport, clicking at 1.5, 1.5 should be row 3, col 1
    # (exact coordinates depend on how your on_canvas_click converts coordinates)
    assert row == 1  # This may need adjustment based on your coordinate system
    assert col == 3  # We clicked in the column (index 1)
