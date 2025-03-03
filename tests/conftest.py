import numpy as np
import pytest

from knitvis import KnittingChart, KnittingColorPalette


@pytest.fixture
def heart_pattern():
    """Creates a simple heart-shaped pattern."""
    return np.array([
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ], dtype=bool)


@pytest.fixture
def heart_chart(heart_pattern):
    """Creates a KnittingChart with a heart pattern in red."""
    stitches = np.array(heart_pattern, dtype=int)
    colors = np.zeros(heart_pattern.shape + (3,), dtype=int)
    colors[heart_pattern] = [255, 0, 0]  # Red heart on black background
    return KnittingChart(stitches, colors)


@pytest.fixture
def checkerboard_pattern():
    """Creates a 6x6 checkerboard pattern of knit and purl stitches."""
    pattern = np.zeros((6, 6), dtype=int)
    pattern[::2, ::2] = 0  # Knit stitches
    pattern[1::2, ::2] = 1  # Purl stitches
    pattern[::2, 1::2] = 1  # Purl stitches
    pattern[1::2, 1::2] = 0  # Knit stitches
    return pattern


@pytest.fixture
def multicolor_checkerboard_chart(checkerboard_pattern):
    """Creates a multicolor checkerboard chart."""
    pattern = checkerboard_pattern
    colors = np.zeros((6, 6, 3), dtype=int)
    colors[::2, ::2] = [255, 0, 0]     # Red
    colors[1::2, ::2] = [0, 255, 0]    # Green
    colors[::2, 1::2] = [0, 0, 255]    # Blue
    colors[1::2, 1::2] = [255, 255, 0]  # Yellow
    return KnittingChart(pattern, colors)


@pytest.fixture
def all_stitch_types_chart():
    """Creates a chart containing all supported stitch types."""
    pattern = np.arange(9).reshape(3, 3)  # 0-8 covering all stitch types
    colors = np.zeros((3, 3, 3), dtype=int)

    # Assign different colors based on stitch type
    for i in range(3):
        for j in range(3):
            stitch_type = pattern[i, j] % 9
            if stitch_type == 0:  # K - Knit
                colors[i, j] = [200, 200, 200]
            elif stitch_type == 1:  # P - Purl
                colors[i, j] = [100, 100, 100]
            elif stitch_type == 2:  # YO - Yarn over
                colors[i, j] = [255, 0, 0]
            elif stitch_type == 3:  # K2tog
                colors[i, j] = [0, 255, 0]
            elif stitch_type == 4:  # SSK
                colors[i, j] = [0, 0, 255]
            elif stitch_type == 5:  # C4F
                colors[i, j] = [255, 255, 0]
            elif stitch_type == 6:  # C4B
                colors[i, j] = [0, 255, 255]
            elif stitch_type == 7:  # BO
                colors[i, j] = [255, 0, 255]
            elif stitch_type == 8:  # CO
                colors[i, j] = [128, 0, 0]

    return KnittingChart(pattern, colors)


@pytest.fixture
def demo_chart():
    """Creates a complex demo chart with multiple stitch types and a color gradient."""
    pattern = np.zeros((10, 10), dtype=int)

    # Create a checkered pattern in the middle
    pattern[2:8, 2:8] = np.indices((6, 6)).sum(0) % 2

    # Add some yarn overs around the border
    pattern[4, 1] = 2  # YO left
    pattern[4, 8] = 2  # YO right
    pattern[1, 4] = 2  # YO top
    pattern[8, 4] = 2  # YO bottom

    # Add some decreases
    pattern[3, 3] = 3  # K2tog
    pattern[3, 6] = 4  # SSK
    pattern[6, 3] = 4  # SSK
    pattern[6, 6] = 3  # K2tog

    # Create colors with a gradient
    colors = np.zeros((10, 10, 3), dtype=int)
    for i in range(10):
        for j in range(10):
            dist = np.sqrt((i - 4.5)**2 + (j - 4.5)**2)
            # Create a circular gradient
            if dist < 5:
                factor = 1.0 - dist/5.0
                colors[i, j] = [int(255 * factor), 0, int(255 * (1-factor))]
            else:
                colors[i, j] = [0, 0, 0]

    return KnittingChart(pattern, colors)


@pytest.fixture
def sample_color_palette():
    """Creates a sample knitting palette with test colors."""
    colors = [(255, 255, 255), (255, 255, 254), (0, 0, 0), (128, 128, 128)]
    return KnittingColorPalette(colors)


@pytest.fixture
def sample_knitting_chart():
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


# Add support for --no-interactive option
def pytest_addoption(parser):
    parser.addoption("--no-interactive", action="store_true",
                     default=True, help="Skip interactive demos")
