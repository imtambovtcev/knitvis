import pytest
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from knitvis.gui.widgets.chart_navigation import ChartNavigationWidget


@pytest.fixture
def chart_navigation(qtbot):
    """Create a ChartNavigationWidget for testing."""
    widget = ChartNavigationWidget()
    qtbot.addWidget(widget)
    return widget


def test_chart_navigation_initialization(chart_navigation):
    """Test that the ChartNavigationWidget initializes correctly."""
    # Check that widgets are created
    assert chart_navigation.row_pos is not None
    assert chart_navigation.col_pos is not None
    assert chart_navigation.row_zoom_slider is not None
    assert chart_navigation.col_zoom_slider is not None
    assert chart_navigation.viewport_display is not None


def test_chart_navigation_viewport_change_signal(qtbot, chart_navigation):
    """Test that viewport changes emit the correct signal."""
    # Create a signal spy
    with qtbot.waitSignal(chart_navigation.viewportChanged) as spy:
        chart_navigation.row_pos.setValue(5)

    # Check signal parameters
    row, col, row_zoom, col_zoom = spy.args
    assert row == 5


def test_chart_navigation_update_limits(chart_navigation):
    """Test that navigation limits are updated correctly based on chart size."""
    # Set up a chart size
    chart_rows = 30
    chart_cols = 40

    # Update navigation limits
    chart_navigation.update_navigation_limits(chart_rows, chart_cols)

    # Check that zoom sliders' maximum values match chart dimensions
    assert chart_navigation.row_zoom_slider.maximum() == chart_rows
    assert chart_navigation.col_zoom_slider.maximum() == chart_cols

    # Set zoom levels
    chart_navigation.row_zoom_slider.setValue(10)
    chart_navigation.col_zoom_slider.setValue(15)

    # Update limits again after zoom level changes
    chart_navigation.update_navigation_limits(chart_rows, chart_cols)

    # Calculate expected maximum values
    expected_row_max = chart_rows - 10
    expected_col_max = chart_cols - 15

    # Check scrollbar ranges
    assert chart_navigation.row_pos.maximum() == expected_row_max
    assert chart_navigation.col_pos.maximum() == expected_col_max


def test_chart_navigation_viewport_display(chart_navigation):
    """Test that viewport display shows the correct information."""
    # Set up chart size and position
    chart_navigation.chart_rows = 30
    chart_navigation.chart_cols = 40
    chart_navigation.row_pos.setValue(5)
    chart_navigation.col_pos.setValue(10)
    chart_navigation.row_zoom_slider.setValue(10)
    chart_navigation.col_zoom_slider.setValue(15)

    # Manually trigger viewport display update
    chart_navigation._update_viewport_display()

    # Check display content (format: "Rows 6-15 | Cols 11-25")
    display_text = chart_navigation.viewport_display.text()
    assert "Rows 6-15" in display_text
    assert "Cols 11-25" in display_text
