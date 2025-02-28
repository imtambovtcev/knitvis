import pytest
import numpy as np
import matplotlib.pyplot as plt
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
