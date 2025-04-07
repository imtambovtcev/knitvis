import matplotlib.pyplot as plt
import numpy as np
import pytest

from knitvis import KnittingChart, KnittingColorPalette


def test_pattern_assignment(sample_knitting_chart):
    """Ensures the pattern is assigned correctly."""
    assert sample_knitting_chart.pattern[0, 0] == 0  # 'K'
    assert sample_knitting_chart.pattern[1, 2] == 2  # 'YO'
    assert sample_knitting_chart.pattern[2, 1] == 3  # 'K2tog'


def test_color_assignment(sample_knitting_chart):
    """Ensures unique colors are correctly mapped to indices in the palette."""
    assert sample_knitting_chart.color_indices.shape == sample_knitting_chart.pattern.shape
    unique_colors = np.unique(sample_knitting_chart.color_indices)
    # All unique colors should be in the palette
    assert len(unique_colors) == len(
        sample_knitting_chart.color_palette.full_names)


def test_get_color_from_palette(sample_knitting_chart):
    """Ensures the assigned color indices correctly map to colors in the palette."""
    for i in range(sample_knitting_chart.rows):
        for j in range(sample_knitting_chart.cols):
            color_index = sample_knitting_chart.color_indices[i, j]
            color_from_palette = sample_knitting_chart.color_palette.get_color_rgb_by_index(
                color_index)
            assert isinstance(color_from_palette, tuple)
            assert len(color_from_palette) == 3  # Ensure it's an RGB tuple


def test_chart_display(sample_knitting_chart):
    """Runs the display function to ensure no exceptions occur."""
    try:
        fig = sample_knitting_chart.display_chart()
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
        assert chart.color_palette.get_color_rgb_by_index(color_index) == color

    # Ensure the color index mapping is correct
    for i in range(chart.rows):
        for j in range(chart.cols):
            expected_color = tuple(colors[i, j])
            color_index = chart.color_indices[i, j]
            assert chart.color_palette.get_color_rgb_by_index(
                color_index) == expected_color


def test_get_symbolic_pattern(sample_knitting_chart):
    """Tests if the symbolic representation of the pattern is correctly returned."""
    expected_symbols = np.array([
        ['V', '●', 'V', '●'],
        ['●', 'V', 'O', 'V'],
        ['V', '/', '\\', 'V']
    ])
    symbolic_pattern = sample_knitting_chart.get_symbolic_pattern()

    assert symbolic_pattern.shape == sample_knitting_chart.pattern.shape
    assert np.array_equal(symbolic_pattern, expected_symbols)


def test_get_text_pattern(sample_knitting_chart):
    """Tests if the text representation of the pattern is correctly returned."""
    expected_text = np.array([
        ['K', 'P', 'K', 'P'],
        ['P', 'K', 'YO', 'K'],
        ['K', 'K2tog', 'SSK', 'K']
    ])
    text_pattern = sample_knitting_chart.get_text_pattern()

    assert text_pattern.shape == sample_knitting_chart.pattern.shape
    assert np.array_equal(text_pattern, expected_text)


def test_get_colors_tags(sample_knitting_chart):
    """Tests if the symbolic color representation matches the original colors."""
    expected_colors = np.array([['W', 'Gy2', 'R', 'Gr2'],
                                ['Bl', 'Gy', 'Pi', 'O'],
                                ['P', 'Br', 'Y', 'Gr']])  # Expected NxMx3 color array

    symbolic_colors = sample_knitting_chart.get_colors_tags()

    assert symbolic_colors.shape == sample_knitting_chart.color_indices.shape
    assert np.array_equal(symbolic_colors, expected_colors)


def test_get_chart_slice(sample_knitting_chart):
    """Tests retrieving a sub-chart using slicing."""
    sliced_chart = sample_knitting_chart[:2,
                                         1:]  # Take first two rows, columns 1 onwards

    # Must return a KnittingChart
    assert isinstance(sliced_chart, KnittingChart)
    assert sliced_chart.pattern.shape == (2, 3)  # Ensure shape is correct
    assert np.array_equal(sliced_chart.pattern,
                          sample_knitting_chart.pattern[:2, 1:])  # Pattern check

    # Ensure color representations match
    expected_colors = sample_knitting_chart.get_colors_rgb()[:2, 1:]
    sliced_colors = sliced_chart.get_colors_rgb()
    assert np.array_equal(sliced_colors, expected_colors)


def test_set_chart_slice(sample_knitting_chart):
    """Tests modifying a part of the knitting chart using another KnittingChart."""
    new_pattern = np.array([[3, 4], [4, 3]])  # New stitch pattern
    new_colors = np.array([
        [[50, 100, 150], [200, 150, 100]],  # RGB for new colors
        [[255, 0, 0], [0, 255, 0]]
    ])  # 2×2×3 color array

    new_chart = KnittingChart(new_pattern, new_colors)

    # Replace the top-left 2×2 section
    sample_knitting_chart[:2, :2] = new_chart

    # Ensure pattern is updated
    assert np.array_equal(sample_knitting_chart.pattern[:2, :2], new_pattern)

    # Ensure color values match after transformation
    updated_colors = sample_knitting_chart.get_colors_rgb()[:2, :2]
    assert np.array_equal(updated_colors, new_colors)


def test_invalid_chart_assignment(sample_knitting_chart):
    """Tests that invalid assignment raises errors."""
    invalid_chart = np.array([[0, 1], [1, 0]])  # Not a KnittingChart instance

    with pytest.raises(TypeError):
        sample_knitting_chart[:2, :2] = invalid_chart  # Should raise TypeError

    # Ensure shape mismatch is caught
    mismatched_chart = KnittingChart(np.array([[3, 4, 5]]), colors=(255, 0, 0))

    with pytest.raises(ValueError):
        # Should raise ValueError
        sample_knitting_chart[:2, :2] = mismatched_chart


def test_invalid_indexing(sample_knitting_chart):
    """Tests that invalid indexing raises errors."""
    with pytest.raises(TypeError):
        sample_knitting_chart["invalid"]  # Invalid key type

    with pytest.raises(IndexError):
        sample_knitting_chart[100, 100]  # Out-of-bounds index


def test_to_dict(sample_knitting_chart):
    """Tests conversion of chart to dictionary format."""
    data = sample_knitting_chart.to_dict()

    # Check dictionary structure
    assert 'pattern' in data
    assert 'color_tags' in data
    assert 'palette' in data

    # Check pattern content (should be text form)
    assert data['pattern'][0][0] == 'K'
    assert data['pattern'][0][1] == 'P'

    # Check color tags exist and match palette
    assert isinstance(data['color_tags'][0][0], str)
    assert all(tag in sample_knitting_chart.color_palette.short_tags
               for row in data['color_tags']
               for tag in row)


def test_from_dict(sample_knitting_chart):
    """Tests creation of chart from dictionary format."""
    original_data = sample_knitting_chart.to_dict()
    reconstructed_chart = KnittingChart.from_dict(original_data)

    # Check pattern matches
    np.testing.assert_array_equal(
        reconstructed_chart.get_text_pattern(),
        sample_knitting_chart.get_text_pattern()
    )

    # Check colors match
    np.testing.assert_array_equal(
        reconstructed_chart.get_colors_tags(),
        sample_knitting_chart.get_colors_tags()
    )


def test_json_roundtrip(sample_knitting_chart, tmp_path):
    """Tests saving to and loading from JSON file."""
    # Create temporary file path
    json_path = tmp_path / "test_chart.json"

    # Save to JSON
    sample_knitting_chart.save_to_json(json_path)

    # Load from JSON
    loaded_chart = KnittingChart.from_json(json_path)

    # Verify pattern matches
    np.testing.assert_array_equal(
        loaded_chart.get_text_pattern(),
        sample_knitting_chart.get_text_pattern()
    )

    # Verify colors match
    np.testing.assert_array_equal(
        loaded_chart.get_colors_tags(),
        sample_knitting_chart.get_colors_tags()
    )


def test_malformed_dict():
    """Tests handling of malformed dictionary data."""
    # Missing pattern
    with pytest.raises(KeyError):
        KnittingChart.from_dict({'color_tags': [], 'palette': {}})

    # Invalid stitch names
    bad_data = {
        'pattern': [['INVALID', 'K']],
        'color_tags': [['W', 'B']],
        'palette': {'colors': [[255, 255, 255], [0, 0, 0]],
                    'full_names': ['White', 'Black'],
                    'short_tags': ['W', 'B']}
    }
    chart = KnittingChart.from_dict(bad_data)
    assert chart.pattern[0][0] == -1  # Invalid stitch should be -1


def test_get_stitch(sample_knitting_chart):
    """Tests retrieving stitch type and color at a specific position."""
    # Get stitch at position (0, 0) - should be 'K' (knit) with white color
    stitch_type, color_rgb = sample_knitting_chart.get_stitch(0, 0)
    assert stitch_type == 'K'
    assert color_rgb == (255, 255, 255)

    # Get stitch at position (1, 2) - should be 'YO' with pink color
    stitch_type, color_rgb = sample_knitting_chart.get_stitch(1, 2)
    assert stitch_type == 'YO'
    assert color_rgb == (255, 182, 193)

    # Test out of bounds
    with pytest.raises(IndexError):
        sample_knitting_chart.get_stitch(100, 100)


def test_set_stitch(sample_knitting_chart):
    """Tests setting stitch type and color at a specific position."""
    # Set only stitch type
    sample_knitting_chart.set_stitch(0, 0, stitch_type='P')
    assert sample_knitting_chart.pattern[0, 0] == 1  # 'P' has index 1
    stitch_type, old_color = sample_knitting_chart.get_stitch(0, 0)
    assert stitch_type == 'P'

    # Set only color
    new_color = (100, 100, 255)  # Light blue
    sample_knitting_chart.set_stitch(0, 0, color_rgb=new_color)
    stitch_type, color_rgb = sample_knitting_chart.get_stitch(0, 0)
    assert color_rgb == new_color
    assert stitch_type == 'P'  # Stitch type should remain unchanged

    # Set both stitch type and color
    sample_knitting_chart.set_stitch(
        1, 1, stitch_type='YO', color_rgb=(255, 0, 255))
    stitch_type, color_rgb = sample_knitting_chart.get_stitch(1, 1)
    assert stitch_type == 'YO'
    assert color_rgb == (255, 0, 255)

    # Test invalid stitch type
    with pytest.raises(ValueError):
        sample_knitting_chart.set_stitch(0, 0, stitch_type='Invalid')

    # Test out of bounds
    with pytest.raises(IndexError):
        sample_knitting_chart.set_stitch(100, 100, stitch_type='K')


def test_set_stitch_adds_color():
    """Tests that setting a stitch with new color adds it to the palette."""
    # Create a simple chart with a single color
    pattern = np.array([[0, 0], [0, 0]])
    colors = np.array([
        [[255, 0, 0], [255, 0, 0]],  # All red
        [[255, 0, 0], [255, 0, 0]]   # All red
    ])

    chart = KnittingChart(pattern, colors)

    # Verify we have just one color in the palette
    assert chart.color_palette.num_colors == 1

    # Set a stitch with a new color
    new_color = (50, 200, 150)  # A color not in the palette
    chart.set_stitch(0, 0, color_rgb=new_color)

    # Verify color was added to the palette
    assert chart.color_palette.num_colors == 2
    assert chart.color_palette.get_index_by_color(new_color) is not None

    # Verify the stitch now has the new color
    _, color_rgb = chart.get_stitch(0, 0)
    assert color_rgb == new_color


def test_optimize_color_palette():
    """Tests that unused colors are removed from the palette when optimizing."""
    # Create a chart with several colors but use only one
    pattern = np.array([[0, 0], [0, 0]])

    # Create a chart where all positions use the same color
    chart = KnittingChart(pattern, (255, 0, 0))  # All red

    # Replace the color palette with one that has unused colors
    chart.color_palette = KnittingColorPalette([
        (255, 0, 0),    # Red - used by all positions
        (0, 255, 0),    # Green - unused
        (0, 0, 255),    # Blue - unused
    ])

    # Verify initial state
    assert chart.color_palette.num_colors == 3

    # Optimize the palette
    chart.optimize_color_palette()

    # Verify that only the used color remains
    assert chart.color_palette.num_colors == 1
    assert chart.color_palette.get_color_rgb_by_index(0) == (255, 0, 0)


def test_optimize_color_palette_preserves_used_colors():
    """Tests that optimize_color_palette only removes unused colors."""
    # Create a chart with 4 colors, but only 2 are actually used
    pattern = np.array([[0, 0], [0, 0]])
    colors = np.array([
        [[255, 0, 0], [255, 0, 0]],  # All red
        [[255, 0, 0], [255, 0, 0]]   # All red
    ])

    # Create the chart
    chart = KnittingChart(pattern, colors)

    # Replace the palette with one having unused colors
    chart.color_palette = KnittingColorPalette([
        (255, 0, 0),    # Red - used
        (0, 255, 0),    # Green - unused
        (0, 0, 255),    # Blue - unused
        (255, 255, 0)   # Yellow - unused
    ])

    # Set all indices to use the red color (index 0)
    chart.color_indices.fill(0)

    # Optimize the palette
    chart.optimize_color_palette()

    # Should now have only 1 color in palette
    assert chart.color_palette.num_colors == 1
    assert chart.color_palette.get_color_rgb_by_index(0) == (255, 0, 0)

    # All indices should still be 0
    assert np.all(chart.color_indices == 0)


def test_get_colors_rgb(sample_knitting_chart):
    """Tests if the RGB color representation matches the original colors."""
    # Expected colors from the sample_knitting_chart fixture
    expected_colors = np.array([
        [[255, 255, 255], [200, 200, 200], [255, 0, 0], [0, 255, 0]],
        [[0, 0, 255], [128, 128, 128], [255, 182, 193], [255, 165, 0]],
        [[128, 0, 128], [165, 42, 42], [255, 255, 0], [0, 128, 0]]
    ])

    # Get RGB colors from the chart
    rgb_colors = sample_knitting_chart.get_colors_rgb()

    # Check shape and values
    assert rgb_colors.shape == (3, 4, 3)  # 3 rows, 4 columns, 3 RGB values
    assert np.array_equal(rgb_colors, expected_colors)

    # Test with specific ranges
    column_range = (1, 3)
    row_range = (0, 2)
    partial_rgb = sample_knitting_chart.get_colors_rgb(column_range, row_range)

    # Check that the partial slice matches the expected subset
    # Still full shape, just slice is filled
    assert partial_rgb.shape == (2, 2, 3)
    assert np.array_equal(
        partial_rgb,
        expected_colors[row_range[0]:row_range[1],
                        column_range[0]:column_range[1]]
    )
