import pytest
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from knitvis.gui.views import FabricView
from knitvis import KnittingChart


@pytest.fixture
def sample_chart():
    """Create a sample chart for testing"""
    # Create a small test pattern
    pattern = np.zeros((5, 5), dtype=int)
    colors = np.full((5, 5, 3), [200, 200, 200], dtype=int)
    return KnittingChart(pattern, colors)


@pytest.fixture
def sample_chart_with_purl():
    """Create a sample chart with a purl stitch for testing exceptions"""
    # Create a small test pattern with one purl stitch
    pattern = np.zeros((5, 5), dtype=int)
    pattern[2, 2] = 1  # Set one stitch to purl (index 1)
    colors = np.full((5, 5, 3), [200, 200, 200], dtype=int)
    return KnittingChart(pattern, colors)


@pytest.fixture
def fabric_view(qtbot, sample_chart):
    """Create a FabricView with a sample chart for testing."""
    view = FabricView(sample_chart)
    qtbot.addWidget(view)
    return view


def test_fabric_view_initialization(fabric_view):
    """Test that the FabricView initializes correctly with a chart"""
    # Check that the fabric view is created
    assert fabric_view is not None

    # Check that the figure and canvas are created
    assert fabric_view.figure is not None
    assert fabric_view.canvas is not None

    # Check that settings are initialized with default values
    assert 'row_spacing' in fabric_view.settings
    assert 'show_outlines' in fabric_view.settings
    assert fabric_view.settings['row_spacing'] == 0.7  # Default value
    assert fabric_view.settings['show_outlines'] is False  # Default value


def test_fabric_view_update(fabric_view, sample_chart):
    """Test that the view updates when settings are changed"""
    # Change the row spacing setting
    original_spacing = fabric_view.settings['row_spacing']
    fabric_view.settings['row_spacing'] = 0.5

    # Force update and check that the setting was used
    fabric_view.update_view()
    # Check instance variable used in rendering
    assert fabric_view.row_spacing == 0.5

    # Reset for other tests
    fabric_view.settings['row_spacing'] = original_spacing


def test_fabric_view_click_signal(qtbot, fabric_view):
    """Test that clicking on the fabric view emits the correct stitch clicked signal"""
    # Create a signal spy
    with qtbot.waitSignal(fabric_view.stitch_clicked) as spy:
        # Calculate where to click (center of a stitch)
        # We simulate a click by calling the handler directly with mock event data
        class MockEvent:
            xdata = 2.2  # Center of second stitch
            ydata = 4.2  # Near bottom of chart
            button = 1  # Left mouse button
            modifiers = frozenset()  # No keyboard modifiers
            def pos(): return None  # Dummy position method

        # Set row_spacing for the test
        fabric_view.row_spacing = 0.7
        # Call the top-level on_canvas_click method
        fabric_view.on_canvas_click(MockEvent())

    # Get the row and column from the signal
    row, col = spy.args

    # Verify expected coordinates
    assert isinstance(row, int)
    assert isinstance(col, int)
    assert col == 1  # Exact column depends on coordinate conversion
    assert row == 3  # Exact row depends on coordinate conversion

    # Also check that the clicked stitch was selected
    assert (row, col) in fabric_view.selected_stitches


def test_fabric_view_shift_click_selection(qtbot, fabric_view):
    """Test that shift+clicking on the fabric view adds to selection without emitting stitch_clicked"""
    # First click to select a stitch normally
    class MockNormalEvent:
        xdata = 2.2  # First stitch position
        ydata = 4.2
        button = 1  # Left mouse button
        modifiers = frozenset()  # No modifiers
        def pos(): return None  # Dummy position method

    # Set row_spacing for the test
    fabric_view.row_spacing = 0.7

    # Perform the first click
    with qtbot.waitSignal(fabric_view.stitch_clicked):
        fabric_view.on_canvas_click(MockNormalEvent())

    # Now shift-click on a different stitch
    class MockShiftEvent:
        xdata = 3.2  # Second stitch position
        ydata = 3.2
        button = 1  # Left mouse button
        modifiers = frozenset(['shift'])  # Shift key modifier
        def pos(): return None  # Dummy position method

    # Perform the shift click - should NOT emit stitch_clicked
    # Instead, should just add to selection
    with qtbot.assertNotEmitted(fabric_view.stitch_clicked, wait=100):
        fabric_view.on_canvas_click(MockShiftEvent())

    # Should now have two stitches selected
    assert len(fabric_view.selected_stitches) == 2
