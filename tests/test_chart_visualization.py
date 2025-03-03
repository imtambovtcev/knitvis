import numpy as np
import matplotlib.pyplot as plt
import pytest
from matplotlib.collections import PolyCollection
from knitvis import KnittingChart


def test_heart_chart_display(heart_chart):
    """Test the display of a heart pattern."""
    # Test basic chart display
    fig = heart_chart.display_chart(x_axis_ticks_every_n=2)
    assert isinstance(fig, plt.Figure)

    # Test chart with row range
    fig = heart_chart.display_chart(x_axis_ticks_every_n=2,
                                    chart_range=((1, 5), None))
    assert isinstance(fig, plt.Figure)

    # Test chart with column range
    fig = heart_chart.display_chart(x_axis_ticks_every_n=2,
                                    chart_range=(None, (1, 5)))
    assert isinstance(fig, plt.Figure)


def test_heart_chart_render_fabric(heart_chart):
    """Test the fabric rendering of a heart pattern."""
    # Test basic fabric rendering
    fig = heart_chart.render_fabric()
    assert isinstance(fig, plt.Figure)

    # Test fabric with row range
    fig = heart_chart.render_fabric(x_axis_ticks_every_n=2,
                                    chart_range=((1, 5), None))
    assert isinstance(fig, plt.Figure)

    # Test fabric with column range
    fig = heart_chart.render_fabric(x_axis_ticks_every_n=2,
                                    chart_range=(None, (1, 5)))
    assert isinstance(fig, plt.Figure)


def test_render_fabric_color_mapping():
    """Test that colors are correctly mapped in the render_fabric output."""
    # Create a simple pattern with alternating knit/purl stitches
    pattern = np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0]
    ])

    # Create colors where each cell has a unique RGB value
    colors = np.array([
        [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]],
        [[255, 0, 255], [0, 255, 255], [128, 128, 128], [64, 64, 64]]
    ])

    chart = KnittingChart(pattern, colors)

    # Render the fabric
    fig, ax = plt.subplots()
    chart.render_fabric(fig, ax)

    # Check that collections were added to the axis
    collections = [c for c in ax.collections if isinstance(c, PolyCollection)]
    assert len(collections) > 0


def test_multicolor_pattern(multicolor_checkerboard_chart):
    """Test a complex pattern with multiple colors."""
    # Test both visualization methods
    fig1 = multicolor_checkerboard_chart.display_chart()
    assert isinstance(fig1, plt.Figure)

    fig2 = multicolor_checkerboard_chart.render_fabric()
    assert isinstance(fig2, plt.Figure)


def test_visualization_with_custom_ticks():
    """Test visualization with custom tick settings."""
    # Simple 5x5 pattern
    pattern = np.ones((5, 5), dtype=int)  # All purl stitches
    colors = np.ones((5, 5, 3), dtype=int) * 128  # Medium gray

    chart = KnittingChart(pattern, colors)

    # Test with custom tick settings
    fig1 = chart.display_chart(
        x_axis_ticks_every_n=1,
        y_axis_ticks_every_n=1,
        x_axis_ticks_numbers_every_n_tics=2,
        y_axis_ticks_numbers_every_n_ticks=2
    )
    assert isinstance(fig1, plt.Figure)

    fig2 = chart.render_fabric(
        x_axis_ticks_every_n=1,
        y_axis_ticks_every_n=1,
        x_axis_ticks_numbers_every_n_tics=2,
        y_axis_ticks_numbers_every_n_ticks=2
    )
    assert isinstance(fig2, plt.Figure)


def test_visualization_with_no_ticks():
    """Test visualization with no ticks displayed."""
    pattern = np.zeros((3, 3), dtype=int)  # All knit stitches
    colors = np.ones((3, 3, 3), dtype=int) * 200  # Light gray

    chart = KnittingChart(pattern, colors)

    # Test with no ticks
    fig1 = chart.display_chart(
        x_axis_ticks_every_n=0,
        y_axis_ticks_every_n=0
    )
    assert isinstance(fig1, plt.Figure)

    fig2 = chart.render_fabric(
        x_axis_ticks_every_n=0,
        y_axis_ticks_every_n=0
    )
    assert isinstance(fig2, plt.Figure)


def test_visualization_with_custom_axes(heart_chart):
    """Test providing custom axes for visualization."""
    # Create custom figure and axes
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Use custom axes for visualization
    heart_chart.display_chart(fig, axes[0])
    heart_chart.render_fabric(fig, axes[1])

    # Check that both axes have content
    assert len(axes[0].collections) > 0
    assert len(axes[1].collections) > 0


def test_pattern_with_all_stitch_types(all_stitch_types_chart):
    """Test visualization of a pattern with all supported stitch types."""
    # Test display_chart with all stitch types
    fig1 = all_stitch_types_chart.display_chart()
    assert isinstance(fig1, plt.Figure)

    # Test render_fabric with all stitch types
    # Note: render_fabric only supports some stitch types
    fig2 = all_stitch_types_chart.render_fabric()
    assert isinstance(fig2, plt.Figure)
