import pytest
import numpy as np
import matplotlib.pyplot as plt
from knitvis import KnittingChart
from knitvis import KnittingColorPalette


@pytest.fixture
def sample_chart():
    """Creates a sample knitting chart with a predefined pattern and colors."""
    pattern = np.array([
        [0, 1, 0, 1],
        [1, 0, 2, 0],
        [0, 3, 4, 0]
    ])  # Using integers as indices of stitch types

    colors = np.array([
        [[255, 255, 255], [200, 200, 200], [255, 0, 0], [0, 255, 0]],
        [[0, 0, 255], [128, 128, 128], [255, 182, 193], [255, 165, 0]],
        [[128, 0, 128], [165, 42, 42], [255, 255, 0], [0, 128, 0]]
    ])  # N×M×3 color array

    return KnittingChart(pattern, colors)


def test_pattern_assignment(sample_chart):
    """Ensures the pattern is assigned correctly."""
    assert sample_chart.pattern[0, 0] == 0  # 'K'
    assert sample_chart.pattern[1, 2] == 2  # 'YO'
    assert sample_chart.pattern[2, 1] == 3  # 'K2tog'


def test_color_assignment(sample_chart):
    """Ensures unique colors are correctly mapped to indices in the palette."""
    assert sample_chart.color_indices.shape == sample_chart.pattern.shape
    unique_colors = np.unique(sample_chart.color_indices)
    # All unique colors should be in the palette
    assert len(unique_colors) == len(sample_chart.color_palette.full_names)


def test_get_color_from_palette(sample_chart):
    """Ensures the assigned color indices correctly map to colors in the palette."""
    for i in range(sample_chart.rows):
        for j in range(sample_chart.cols):
            color_index = sample_chart.color_indices[i, j]
            color_from_palette = sample_chart.color_palette.get_color_by_index(
                color_index)
            assert isinstance(color_from_palette, tuple)
            assert len(color_from_palette) == 3  # Ensure it's an RGB tuple


def test_chart_display(sample_chart):
    """Runs the display function to ensure no exceptions occur."""
    try:
        fig = sample_chart.display_chart()
        assert fig is not None
        # Ensure output is a Matplotlib figure
        assert isinstance(fig, plt.Figure)
    except Exception as e:
        pytest.fail(f"display_chart() raised an exception: {e}")


def test_custom_color_palette():
    """Tests using a custom set of colors instead of raw RGB values."""
    pattern = np.array([[0, 1], [1, 0]])  # Integer indices for stitches
    colors = np.array([
        [[128, 0, 128], [255, 182, 193]],  # Purple, Pink
        [[0, 255, 255], [255, 165, 0]]  # Cyan, Orange
    ])  # 2×2×3 array

    chart = KnittingChart(pattern, colors)

    # Extract unique colors from input
    unique_colors = [tuple(color)
                     for color in np.unique(colors.reshape(-1, 3), axis=0)]

    # Check if colors in the palette match the unique colors
    for color in unique_colors:
        color_index = chart.color_palette.get_index_by_color(color)
        assert color_index is not None, f"Color {color} not found in palette"
        assert chart.color_palette.get_color_by_index(color_index) == color

    # Ensure the color index mapping is correct
    for i in range(chart.rows):
        for j in range(chart.cols):
            expected_color = tuple(colors[i, j])
            color_index = chart.color_indices[i, j]
            assert chart.color_palette.get_color_by_index(
                color_index) == expected_color


def test_get_symbolic_pattern(sample_chart):
    """Tests if the symbolic representation of the pattern is correctly returned."""
    expected_symbols = np.array([
        ['V', '●', 'V', '●'],
        ['●', 'V', 'O', 'V'],
        ['V', '/', '\\', 'V']
    ])
    symbolic_pattern = sample_chart.get_symbolic_pattern()

    assert symbolic_pattern.shape == sample_chart.pattern.shape
    assert np.array_equal(symbolic_pattern, expected_symbols)


def test_get_text_pattern(sample_chart):
    """Tests if the text representation of the pattern is correctly returned."""
    expected_text = np.array([
        ['K', 'P', 'K', 'P'],
        ['P', 'K', 'YO', 'K'],
        ['K', 'K2tog', 'SSK', 'K']
    ])
    text_pattern = sample_chart.get_text_pattern()

    assert text_pattern.shape == sample_chart.pattern.shape
    assert np.array_equal(text_pattern, expected_text)


def test_get_symbolic_colors(sample_chart):
    """Tests if the symbolic color representation matches the original colors."""
    expected_colors = np.array([
        [[255, 255, 255], [200, 200, 200], [255, 0, 0], [0, 255, 0]],
        [[0, 0, 255], [128, 128, 128], [255, 182, 193], [255, 165, 0]],
        [[128, 0, 128], [165, 42, 42], [255, 255, 0], [0, 128, 0]]
    ])  # Expected NxMx3 color array

    symbolic_colors = sample_chart.get_symbolic_colors()

    assert symbolic_colors.shape == sample_chart.color_indices.shape + (3,)
    assert np.array_equal(symbolic_colors, expected_colors)


def test_get_chart_slice(sample_chart):
    """Tests retrieving a sub-chart using slicing."""
    sliced_chart = sample_chart[:2,
                                1:]  # Take first two rows, columns 1 onwards

    # Must return a KnittingChart
    assert isinstance(sliced_chart, KnittingChart)
    assert sliced_chart.pattern.shape == (2, 3)  # Ensure shape is correct
    assert np.array_equal(sliced_chart.pattern,
                          sample_chart.pattern[:2, 1:])  # Pattern check

    # Ensure color representations match
    expected_colors = sample_chart.get_symbolic_colors()[:2, 1:]
    sliced_colors = sliced_chart.get_symbolic_colors()
    assert np.array_equal(sliced_colors, expected_colors)


def test_set_chart_slice(sample_chart):
    """Tests modifying a part of the knitting chart using another KnittingChart."""
    new_pattern = np.array([[3, 4], [4, 3]])  # New stitch pattern
    new_colors = np.array([
        [[50, 100, 150], [200, 150, 100]],  # RGB for new colors
        [[255, 0, 0], [0, 255, 0]]
    ])  # 2×2×3 color array

    new_chart = KnittingChart(new_pattern, new_colors)

    sample_chart[:2, :2] = new_chart  # Replace the top-left 2×2 section

    # Ensure pattern is updated
    assert np.array_equal(sample_chart.pattern[:2, :2], new_pattern)

    # Ensure color values match after transformation
    updated_colors = sample_chart.get_symbolic_colors()[:2, :2]
    assert np.array_equal(updated_colors, new_colors)


def test_invalid_chart_assignment(sample_chart):
    """Tests that invalid assignment raises errors."""
    invalid_chart = np.array([[0, 1], [1, 0]])  # Not a KnittingChart instance

    with pytest.raises(TypeError):
        sample_chart[:2, :2] = invalid_chart  # Should raise TypeError

    # Ensure shape mismatch is caught
    mismatched_chart = KnittingChart(np.array([[3, 4, 5]]), colors=(255, 0, 0))

    with pytest.raises(ValueError):
        sample_chart[:2, :2] = mismatched_chart  # Should raise ValueError


def test_invalid_indexing(sample_chart):
    """Tests that invalid indexing raises errors."""
    with pytest.raises(TypeError):
        sample_chart["invalid"]  # Invalid key type

    with pytest.raises(IndexError):
        sample_chart[100, 100]  # Out-of-bounds index
