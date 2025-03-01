import matplotlib.pyplot as plt
import numpy as np
import pytest

from knitvis import KnittingColorPalette


@pytest.fixture
def sample_palette():
    """Creates a sample knitting palette with test colors."""
    colors = [(255, 255, 255), (255, 255, 254), (0, 0, 0), (128, 128, 128)]
    return KnittingColorPalette(colors)


def test_color_assignment(sample_palette):
    """Tests if colors are correctly assigned unique names."""
    assigned_names = sample_palette.full_names
    assert "White" in assigned_names
    assert "White2" in assigned_names
    assert "Black" in assigned_names
    assert "Gray" in assigned_names


def test_get_color_by_name(sample_palette):
    """Tests retrieving colors by full name."""
    assert sample_palette.get_color_by_name("White") == (255, 255, 255)
    assert sample_palette.get_color_by_name("White2") == (255, 255, 254)
    assert sample_palette.get_color_by_name("Black") == (0, 0, 0)
    assert sample_palette.get_color_by_name("Gray") == (128, 128, 128)


def test_get_color_by_tag(sample_palette):
    """Tests retrieving colors by short tag."""
    assert sample_palette.get_color_by_tag("W") == (255, 255, 255)
    assert sample_palette.get_color_by_tag("W2") == (255, 255, 254)
    assert sample_palette.get_color_by_tag("B") == (0, 0, 0)
    assert sample_palette.get_color_by_tag("Gy") == (128, 128, 128)


def test_invalid_color_retrieval(sample_palette):
    """Tests retrieval of a nonexistent color."""
    assert sample_palette.get_color_by_name("Red") is None
    assert sample_palette.get_color_by_tag("R") is None


def test_unique_short_tags(sample_palette):
    """Ensures that each assigned color has a unique short tag."""
    assert len(set(sample_palette.short_tags)) == len(
        sample_palette.short_tags)  # Ensures uniqueness


def test_display_palette(sample_palette):
    """Runs the display function to ensure no errors occur."""
    try:
        fig = sample_palette.display_palette()  # Ensure the function runs
        assert fig is not None  # Ensure a valid figure is returned
        # Ensure output is a Matplotlib figure
        assert isinstance(fig, plt.Figure)
    except Exception as e:
        pytest.fail(f"display_palette() raised an exception: {e}")


def test_palette_str(sample_palette):
    """Tests the string representation of the palette."""
    output = str(sample_palette)
    assert "White    -> W   -> (255, 255, 255)" in output
    assert "White2   -> W2  -> (255, 255, 254)" in output
    assert "Black    -> B   -> (0, 0, 0)" in output
    assert "Gray     -> Gy  -> (128, 128, 128)" in output


def test_to_dict(sample_palette):
    """Tests conversion of palette to dictionary format."""
    data = sample_palette.to_dict()

    # Check dictionary structure
    assert 'colors' in data
    assert 'full_names' in data
    assert 'short_tags' in data

    # Verify content
    assert data['colors'][0] == [255, 255, 255]  # First color
    assert 'White' in data['full_names']  # Check name exists
    assert 'W' in data['short_tags']  # Check tag exists

    # Verify lengths match
    assert len(data['colors']) == len(
        data['full_names']) == len(data['short_tags'])


def test_from_dict(sample_palette):
    """Tests creation of palette from dictionary format."""
    original_data = sample_palette.to_dict()
    reconstructed_palette = KnittingColorPalette.from_dict(original_data)

    # Check all colors match
    np.testing.assert_array_equal(
        reconstructed_palette.assigned_colors,
        sample_palette.assigned_colors
    )

    # Check names and tags match
    assert np.array_equal(reconstructed_palette.full_names,
                          sample_palette.full_names)
    assert np.array_equal(reconstructed_palette.short_tags,
                          sample_palette.short_tags)


def test_json_roundtrip(sample_palette, tmp_path):
    """Tests saving to and loading from JSON file."""
    # Create temporary file path
    json_path = tmp_path / "test_palette.json"

    # Save to JSON
    sample_palette.save_to_json(json_path)

    # Load from JSON
    loaded_palette = KnittingColorPalette.from_json(json_path)

    # Verify all data matches
    np.testing.assert_array_equal(
        loaded_palette.assigned_colors,
        sample_palette.assigned_colors
    )
    assert np.array_equal(loaded_palette.full_names, sample_palette.full_names)
    assert np.array_equal(loaded_palette.short_tags, sample_palette.short_tags)


def test_malformed_dict():
    """Tests handling of malformed dictionary data."""
    # Missing required keys
    with pytest.raises(KeyError):
        KnittingColorPalette.from_dict(
            {'colors': []})  # Missing names and tags

    # Empty data
    empty_data = {
        'colors': [],
        'full_names': [],
        'short_tags': []
    }
    palette = KnittingColorPalette.from_dict(empty_data)
    assert palette.num_colors == 0

    # Mismatched lengths
    bad_data = {
        'colors': [[255, 255, 255]],
        'full_names': ['White', 'Extra'],
        'short_tags': ['W']
    }
    with pytest.raises(ValueError):
        KnittingColorPalette.from_dict(bad_data)


def test_add_color(sample_palette):
    """Tests adding a new color to the palette."""
    initial_count = sample_palette.num_colors

    # Add a new color
    new_color = (255, 0, 255)  # Magenta
    index = sample_palette.add_color(new_color)

    # Verify color was added
    assert sample_palette.num_colors == initial_count + 1
    assert index == initial_count  # Index should be the previous count
    assert sample_palette.get_color_by_index(index) == new_color

    # Verify naming logic
    # Should be named as a shade of purple
    assert "Purple" in sample_palette.full_names[-1]
    # Short tag should start with P
    assert sample_palette.short_tags[-1].startswith('P')


def test_add_existing_color(sample_palette):
    """Tests adding a color that already exists in the palette."""
    initial_count = sample_palette.num_colors
    existing_color = (0, 0, 0)  # Black, already in the palette

    # Add the existing color
    index = sample_palette.add_color(existing_color)

    # Verify no new color was added
    assert sample_palette.num_colors == initial_count
    assert index < initial_count  # Should return existing index
    assert sample_palette.get_color_by_index(index) == existing_color


def test_color_naming_logic(sample_palette):
    """Tests that colors are named with appropriate incremental suffixes."""
    # Add two more white-like colors
    white1 = (254, 254, 254)
    white2 = (253, 253, 253)

    idx1 = sample_palette.add_color(white1)
    idx2 = sample_palette.add_color(white2)

    # Check naming logic - should be something like White3, White4
    # since White and White2 already exist
    full_name1 = sample_palette.full_names[idx1]
    full_name2 = sample_palette.full_names[idx2]

    assert full_name1.startswith('White')
    assert full_name2.startswith('White')
    assert full_name1 != 'White'  # Should have a number suffix
    assert full_name2 != 'White'
    assert full_name1 != full_name2  # Should be different names
