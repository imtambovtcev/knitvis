import json

import matplotlib.pyplot as plt
import numpy as np

from .palette import KnittingColorPalette


class KnittingChart:
    """Visualize a knitting pattern as a chart.

    The pattern is provided as a NumPy array (N×M) of integers,
    where each integer is an index into STITCH_ORDER (defining the stitch type).

    Colors is optional:
      - None: all cells default to (128,128,128)
      - A single color (tuple/list of length 3): applied uniformly
      - An (N×M×3) array: each cell’s color is specified.

    In the latter case, the unique colors are extracted and a color palette is built.
    Then, the (N×M×3) array is replaced by an (N×M) array of indices referencing the palette.
    """

    # Mapping for stitch symbols
    STITCH_SYMBOLS = {
        'K': 'V',    # Knit stitch
        'P': '●',    # Purl stitch
        'YO': 'O',   # Yarn over
        'K2tog': '/',  # Knit two together (right decrease)
        'SSK': '\\',  # Slip slip knit (left decrease)
        'C4F': 'X',  # Cable Front
        'C4B': 'X',  # Cable Back
        'BO': '-',   # Bind off
        'CO': '_',   # Cast on
    }
    # Fixed ordering: pattern integers correspond to these stitch keys
    STITCH_ORDER = ['K', 'P', 'YO', 'K2tog', 'SSK', 'C4F', 'C4B', 'BO', 'CO']

    DEFAULT_COLOR = np.array([128, 128, 128], dtype=int)

    def __init__(self, pattern, colors=None):
        """
        :param pattern: NumPy array (N, M) with integers for stitch types.
        :param colors: Either None, a single RGB color (length-3), or a NumPy array (N, M, 3).
        """
        self.pattern = np.array(pattern, dtype=int)
        self.rows, self.cols = self.pattern.shape

        # Process colors
        if colors is None:
            default_color = np.array([128, 128, 128], dtype=int)
            colors_array = np.tile(default_color, (self.rows, self.cols, 1))
        else:
            colors = np.array(colors, dtype=int)
            if colors.ndim == 1 and colors.size == 3:
                colors_array = np.tile(colors, (self.rows, self.cols, 1))
            else:
                if colors.shape != (self.rows, self.cols, 3):
                    raise ValueError("Colors array must have shape (N, M, 3)")
                colors_array = colors

        # Extract unique colors and create a palette
        flat_colors = colors_array.reshape(-1, 3)
        unique_colors, inverse = np.unique(
            flat_colors, axis=0, return_inverse=True)
        self.color_palette = KnittingColorPalette(
            [tuple(color) for color in unique_colors])
        self.color_indices = np.array([self.color_palette.get_index_by_color(
            c) for c in flat_colors]).reshape(self.rows, self.cols)

    @staticmethod
    def stitch_to_index(stitch):
        """Converts a stitch symbol (e.g., 'K', 'P') to its index in STITCH_ORDER.

        :param stitch: String representing the stitch type.
        :return: Integer index of the stitch in STITCH_ORDER, or -1 if not found.
        """
        try:
            return KnittingChart.STITCH_ORDER.index(stitch)
        except ValueError:
            return -1  # Returns -1 if the stitch is not found

    def get_symbolic_pattern(self):
        """Returns the knitting pattern as an NxM NumPy array of stitch symbols."""
        symbolic_pattern = np.full(
            self.pattern.shape, '?', dtype='<U2')  # Default to '?'

        for i in range(self.rows):
            for j in range(self.cols):
                stitch_idx = self.pattern[i, j]
                if 0 <= stitch_idx < len(self.STITCH_ORDER):
                    symbolic_pattern[i,
                                     j] = self.STITCH_SYMBOLS[self.STITCH_ORDER[stitch_idx]]

        return symbolic_pattern

    def get_text_pattern(self):
        """Returns the knitting pattern as an NxM NumPy array of stitch names."""
        text_pattern = np.full(self.pattern.shape, 'Unknown',
                               dtype='<U10')  # Default to 'Unknown'

        for i in range(self.rows):
            for j in range(self.cols):
                stitch_idx = self.pattern[i, j]
                if 0 <= stitch_idx < len(self.STITCH_ORDER):
                    text_pattern[i, j] = self.STITCH_ORDER[stitch_idx]

        return text_pattern

    def get_symbolic_colors(self):
        """Returns the knitting chart colors as an NxMx3 NumPy array (RGB format)."""
        symbolic_colors = np.zeros((self.rows, self.cols, 3), dtype=int)

        for i in range(self.rows):
            for j in range(self.cols):
                color_index = self.color_indices[i, j]
                symbolic_colors[i, j] = self.color_palette.get_color_by_index(
                    color_index)

        return symbolic_colors

    def display_chart(self):
        """Visualizes the chart as a grid with stitch symbols and cell colors.

        Returns the Matplotlib figure.
        """
        fig, ax = plt.subplots(figsize=(self.cols * 0.8, self.rows * 0.8))

        for i in range(self.rows):
            for j in range(self.cols):
                # Map the pattern integer to a stitch symbol.
                stitch_idx = self.pattern[i, j]
                if stitch_idx < 0 or stitch_idx >= len(self.STITCH_ORDER):
                    symbol = '?'
                else:
                    stitch_key = self.STITCH_ORDER[stitch_idx]
                    symbol = self.STITCH_SYMBOLS.get(stitch_key, '?')

                # Retrieve the cell color from the palette via its index.
                color_index = self.color_indices[i, j]
                rgb = self.color_palette.get_color_by_index(color_index)

                # Normalize RGB to 0-1 range for Matplotlib.
                normalized_rgb = [c / 255 for c in rgb]

                # Calculate relative luminance to determine text color
                luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
                text_color = "black" if luminance > 128 else "white"

                # Draw the cell rectangle.
                ax.add_patch(plt.Rectangle((j, self.rows - 1 - i), 1, 1,
                                           color=normalized_rgb, edgecolor='black'))

                # Draw the stitch symbol with appropriate text color.
                ax.text(j + 0.5, self.rows - 1 - i + 0.5, symbol,
                        ha='center', va='center', fontsize=12, fontweight='bold',
                        color=text_color)

        ax.set_xlim(0, self.cols)
        ax.set_ylim(0, self.rows)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        return fig

    def __str__(self):
        """Returns a formatted string representation of the knitting chart."""
        pattern_str = "Knitting Chart:\n"

        # Build the pattern grid as symbols
        for i in range(self.rows):
            row_str = " ".join(
                self.STITCH_SYMBOLS.get(
                    self.STITCH_ORDER[self.pattern[i, j]], "?")
                for j in range(self.cols)
            )
            pattern_str += row_str + "\n"

        # Create color chart with tag representation
        color_chart_str = "\nColor Chart:\n"
        for i in range(self.rows):
            row_str = " ".join(
                self.color_palette.short_tags[self.color_indices[i, j]]
                for j in range(self.cols)
            )
            color_chart_str += row_str + "\n"

        # Display color palette with tags instead of numbers
        palette_str = "\nColor Palette:\n"
        for i in range(self.color_palette.num_colors):
            tag = self.color_palette.short_tags[i]
            color = self.color_palette.get_color_by_index(i)
            palette_str += f"  {tag}: {color}\n"

        return pattern_str + color_chart_str + palette_str

    def __getitem__(self, key):
        """Allows NumPy-like slicing for the KnittingChart.

        :param key: A tuple of indices/slices (e.g., `chart[:50,50:]`).
        :return: A new KnittingChart instance with the sliced data.
        """
        if isinstance(key, tuple) and len(key) == 2:
            # Slice pattern
            pattern_slice = self.pattern[key]

            # Convert color indices back to NxMx3 RGB values before slicing
            symbolic_colors = self.get_symbolic_colors()
            color_slice = symbolic_colors[key]  # Apply the same slicing

            return KnittingChart(pattern_slice, colors=color_slice)

        raise TypeError("Indexing must be a tuple of two slices/indices.")

    def __setitem__(self, key, value):
        """Allows modifying the knitting chart using indexing.

        :param key: A tuple of indices/slices (e.g., `chart[:10, :10]`).
        :param value: A KnittingChart instance of matching shape.
        """
        if not isinstance(value, KnittingChart):
            raise TypeError("Value must be an instance of KnittingChart.")

        if isinstance(key, tuple) and len(key) == 2:
            # Ensure the inserted chart has the same shape as the target slice
            target_shape = self.pattern[key].shape
            if value.pattern.shape != target_shape:
                raise ValueError(
                    f"Shape mismatch: expected {target_shape}, got {value.pattern.shape}")

            # Update pattern
            self.pattern[key] = value.pattern

            # Convert the inserted chart's color indices back to RGB for modification
            symbolic_colors = self.get_symbolic_colors()
            # Apply new colors
            symbolic_colors[key] = value.get_symbolic_colors()

            # Recreate KnittingChart with updated colors
            updated_chart = KnittingChart(self.pattern, colors=symbolic_colors)

            # Transfer data back to self
            self.pattern = updated_chart.pattern
            self.color_indices = updated_chart.color_indices
            self.color_palette = updated_chart.color_palette

        else:
            raise TypeError("Indexing must be a tuple of two slices/indices.")

    def to_dict(self):
        """
        Convert the knitting chart to a human-readable dictionary.
        Uses stitch names for pattern and color tags for colors.

        :return: Dictionary containing chart data
        """
        # Convert pattern indices to stitch names
        text_pattern = self.get_text_pattern()

        # Convert color indices to tags
        color_tags = np.empty(self.color_indices.shape, dtype='<U4')
        for i in range(self.rows):
            for j in range(self.cols):
                color_idx = self.color_indices[i, j]
                color_tags[i, j] = self.color_palette.short_tags[color_idx]

        return {
            'pattern': text_pattern.tolist(),
            'color_tags': color_tags.tolist(),
            'palette': self.color_palette.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a new KnittingChart instance from a dictionary.
        Expects stitch names for pattern and color tags for colors.

        :param data: Dictionary containing chart data
        :return: New KnittingChart instance
        """
        # Convert text pattern to indices
        pattern = np.array([[cls.stitch_to_index(stitch) for stitch in row]
                            for row in data['pattern']], dtype=int)

        # Recreate the color palette
        palette = KnittingColorPalette.from_dict(data['palette'])

        # Convert color tags to RGB values
        rows, cols = len(data['color_tags']), len(data['color_tags'][0])
        colors = np.zeros((rows, cols, 3), dtype=int)

        for i in range(rows):
            for j in range(cols):
                tag = data['color_tags'][i][j]
                rgb = palette.get_color_by_tag(tag)
                if rgb is not None:
                    colors[i, j] = rgb
                else:
                    colors[i, j] = cls.DEFAULT_COLOR

        return cls(pattern, colors)

    def save_to_json(self, filepath):
        """
        Save the knitting chart to a JSON file in human-readable format.

        :param filepath: Path to save the JSON file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_json(cls, filepath):
        """
        Create a new KnittingChart instance from a JSON file.

        :param filepath: Path to the JSON file
        :return: New KnittingChart instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
