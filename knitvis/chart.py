import json

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from .palette import KnittingColorPalette


class KnittingChartJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for knitting chart data that formats 2D arrays nicely."""

    def iterencode(self, obj, _one_shot=False):
        """Custom iterencode to format 2D arrays with rows on single lines."""
        if isinstance(obj, dict) and 'pattern' in obj and 'color_tags' in obj:
            # Handle special case of our chart data structure
            chunks = self.iterencode_chart_dict(obj)
            for chunk in chunks:
                yield chunk
        else:
            # Use standard encoding for everything else
            for chunk in super().iterencode(obj, _one_shot=_one_shot):
                yield chunk

    def iterencode_chart_dict(self, chart_dict):
        """Special handling for chart dictionary structure."""
        yield '{\n'

        # Track if we need a comma between items
        first_item = True

        for key, value in chart_dict.items():
            if not first_item:
                yield ',\n'
            else:
                first_item = False

            # Add the key
            yield f'  {json.dumps(key)}: '

            # Special format for 2D arrays (pattern and color_tags)
            if key in ['pattern', 'color_tags'] and isinstance(value, list) and value and isinstance(value[0], list):
                yield '[\n'

                # Process each row
                for i, row in enumerate(value):
                    row_json = json.dumps(row)
                    if i < len(value) - 1:
                        yield f'    {row_json},\n'
                    else:
                        yield f'    {row_json}\n'

                yield '  ]'
            elif key == 'palette':
                # Special handling for palette to ensure proper formatting of nested colors
                palette_dict = value
                yield '{\n'

                # Track if we need a comma between palette items
                first_palette_item = True

                for palette_key, palette_value in palette_dict.items():
                    if not first_palette_item:
                        yield ',\n'
                    else:
                        first_palette_item = False

                    # Add the palette key
                    yield f'    {json.dumps(palette_key)}: '

                    # Special handling for colors array
                    if palette_key == 'colors':
                        yield '[\n'
                        for j, color in enumerate(palette_value):
                            color_json = json.dumps(color)
                            if j < len(palette_value) - 1:
                                yield f'      {color_json},\n'
                            else:
                                yield f'      {color_json}\n'
                        yield '    ]'
                    else:
                        # For full_names and short_tags
                        yield json.dumps(palette_value)

                yield '\n  }'
            else:
                # For other values
                yield json.dumps(value)

        yield '\n}'


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
        """Converts a stitch symbol (e.g., 'K', 'P') or a list of them to its index/indices in STITCH_ORDER.

        :param stitch: String or list of strings representing the stitch type(s).
        :return: Integer index or list of indices of the stitch(es) in STITCH_ORDER, or -1 if not found.
        """
        if isinstance(stitch, str):
            try:
                return KnittingChart.STITCH_ORDER.index(stitch)
            except ValueError:
                return -1  # Returns -1 if the stitch is not found
        elif isinstance(stitch, list):
            return [KnittingChart.STITCH_ORDER.index(s) if s in KnittingChart.STITCH_ORDER else -1 for s in stitch]
        else:
            raise TypeError("Input must be a string or a list of strings")

    @staticmethod
    def index_to_stitch(index):
        """Converts a stitch index or list of indices to its symbol(s) (e.g., 0 -> 'K', 1 -> 'P').

        :param index: Integer index or list of indices of the stitch in STITCH_ORDER.
        :return: String representing the stitch type, or list of strings, or 'Unknown' if not found.
        """
        if isinstance(index, (int, np.integer)):
            if 0 <= index < len(KnittingChart.STITCH_ORDER):
                return KnittingChart.STITCH_ORDER[index]
            return 'Unknown'
        elif isinstance(index, list):
            return [KnittingChart.STITCH_ORDER[i] if 0 <= i < len(KnittingChart.STITCH_ORDER) else 'Unknown' for i in index]
        else:
            raise TypeError("Input must be an integer or a list of integers")

    @staticmethod
    def index_to_symbol(index):
        """Converts a stitch index or list of indices to its symbol(s) (e.g., 0 -> 'V', 1 -> '●').
        :param index: Integer index or list of indices of the stitch in STITCH_ORDER.
        :return: String representing the stitch symbol, or list of strings, or '?' if not found.
        """
        if isinstance(index, (int, np.integer)):
            stitch = KnittingChart.index_to_stitch(index)
            return KnittingChart.STITCH_SYMBOLS.get(stitch, '?')
        elif isinstance(index, list):
            return [KnittingChart.STITCH_SYMBOLS.get(KnittingChart.index_to_stitch(i), '?') for i in index]
        else:
            raise TypeError("Input must be an integer or a list of integers")

    def get_symbolic_pattern(self, column_range=None, row_range=None):
        """Returns the knitting pattern as an NxM NumPy array of stitch symbols."""

        column_range = column_range or (0, self.cols)
        row_range = row_range or (0, self.rows)

        symbolic_pattern = np.full(
            self.pattern.shape, '?', dtype='<U2')  # Default to '?'

        for i in range(row_range[0], row_range[1]):
            for j in range(column_range[0], column_range[1]):
                stitch_idx = self.pattern[i, j]
                symbolic_pattern[i, j] = self.index_to_symbol(stitch_idx)

        return symbolic_pattern

    def get_text_pattern(self, column_range=None, row_range=None):
        """Returns the knitting pattern as an NxM NumPy array of stitch names."""
        column_range = column_range or (0, self.cols)
        row_range = row_range or (0, self.rows)

        # Default to 'Unknown'
        text_pattern = np.full(self.pattern.shape, 'Unknown', dtype='<U10')

        for i in range(row_range[0], row_range[1]):
            for j in range(column_range[0], column_range[1]):
                stitch_idx = self.pattern[i, j]
                text_pattern[i, j] = self.index_to_stitch(stitch_idx)

        return text_pattern

    def get_symbolic_colors(self, column_range=None, row_range=None):
        """Returns the knitting chart colors as an NxMx3 NumPy array (RGB format)."""
        column_range = column_range or (0, self.cols)
        row_range = row_range or (0, self.rows)

        symbolic_colors = np.zeros((self.rows, self.cols, 3), dtype=int)

        for i in range(row_range[0], row_range[1]):
            for j in range(column_range[0], column_range[1]):
                color_index = self.color_indices[i, j]
                symbolic_colors[i, j] = self.color_palette.get_color_by_index(
                    color_index)

        return symbolic_colors

    def get_rgb_colors(self, column_range=None, row_range=None):
        """Returns the knitting chart colors as an NxMx3 NumPy array (RGB format)."""
        column_range = column_range or (0, self.cols)
        row_range = row_range or (0, self.rows)

        rgb_colors = np.zeros((self.rows, self.cols, 3), dtype=int)

        for i in range(row_range[0], row_range[1]):
            for j in range(column_range[0], column_range[1]):
                color_index = self.color_indices[i, j]
                rgb_colors[i, j] = self.color_palette.get_color_by_index(
                    color_index)

        return rgb_colors

    def display_chart(self, fig=None, ax=None, ratio=None, fontsize=12, fontweight='bold', chart_range: tuple[tuple[int, int] | None, tuple[int, int] | None] | None = None,
                      x_axis_ticks_every_n: int | None = 1, y_axis_ticks_every_n: int | None = 1, x_axis_ticks_numbers_every_n_tics: int | None = 1, y_axis_ticks_numbers_every_n_ticks: int | None = 1):
        """Visualizes the chart as a grid with stitch symbols and cell colors.

        Returns the Matplotlib figure.
        """

        range_row = (
            0, self.rows) if chart_range is None or chart_range[0] is None else chart_range[0]
        range_col = (
            0, self.cols) if chart_range is None or chart_range[1] is None else chart_range[1]

        print(f'range_row: {range_row}, range_col: {range_col}')

        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=(
                abs(range_col[1]-range_col[0]) * 0.8, abs(range_row[1]-range_row[0]) * 0.8))

        stitches_symbols = self.get_symbolic_pattern(
            column_range=range_col, row_range=range_row)

        stitches_colors = self.get_rgb_colors(
            column_range=range_col, row_range=range_row)

        for i in range(range_row[0], range_row[1]):
            for j in range(range_col[0], range_col[1]):
                # Map the pattern integer to a stitch symbol.
                symbol = stitches_symbols[i-range_row[0], j-range_col[0]]
                rgb = stitches_colors[i-range_row[0], j-range_col[0]]

                # Normalize RGB to 0-1 range for Matplotlib.
                normalized_rgb = [c / 255 for c in rgb]

                # Calculate relative luminance to determine text color
                luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
                text_color = "black" if luminance > 128 else "white"

                # Draw the cell rectangle.
                ax.add_patch(plt.Rectangle((j+0.5, i+0.5), 1, 1,
                                           color=normalized_rgb, edgecolor='black'))

                # Draw the stitch symbol with appropriate text color.
                if isinstance(fontsize, (int, float)) and fontsize > 0:
                    ax.text(j+1, i+1, symbol,
                            ha='center', va='center', fontsize=fontsize, fontweight=fontweight, color=text_color)

        ax.set_xlim(0.5+range_col[0], 0.5+range_col[1])
        ax.set_ylim(0.5+range_row[1], 0.5+range_row[0])

        if x_axis_ticks_every_n > 0:
            ax.set_xticks(
                np.arange(range_col[0]+1, range_col[1]+1, x_axis_ticks_every_n))
            if x_axis_ticks_numbers_every_n_tics > 0:
                tick_labels = np.arange(
                    range_col[0]+1, range_col[1]+1, x_axis_ticks_every_n)
                tick_labels = tick_labels.astype(str)
                tick_labels[np.where(tick_labels.astype(int) %
                                     x_axis_ticks_numbers_every_n_tics != 0)] = ''
                ax.set_xticklabels(tick_labels)
        else:
            ax.set_xticks([])

        if y_axis_ticks_every_n > 0:
            ax.set_yticks(
                np.arange(range_row[0]+1, range_row[1]+1, y_axis_ticks_every_n))
            if y_axis_ticks_numbers_every_n_ticks > 0:
                tick_labels = np.arange(
                    range_row[0]+1, range_row[1]+1, y_axis_ticks_every_n)
                tick_labels = tick_labels.astype(str)
                tick_labels[np.where(tick_labels.astype(int) %
                                     y_axis_ticks_numbers_every_n_ticks != 0)] = ''
                ax.set_yticklabels(tick_labels)
        else:
            ax.set_yticks([])

        ax.set_frame_on(False)
        if ratio:
            ax.set_aspect(ratio)

        return fig

    def render_fabric(self, figsize=None, ratio=0.7, padding=0.01, show_outlines=False, ax=None):
        """
        Renders a knitting chart as a fabric with V-shaped stitches.

        Parameters:
        -----------
        figsize : tuple, optional
            Figure dimensions (width, height) in inches
        ratio : float
            Vertical positioning ratio between rows (default=0.7)
        padding : float
            Padding between stitches (default=0.01)
        show_outlines : bool
            Whether to show black outlines on stitches (default=False)
        ax : matplotlib.axes.Axes, optional
            An existing axes to draw on. If None, a new figure and axes will be created.

        Returns:
        --------
        matplotlib.figure.Figure
            The rendered fabric figure
        """
        y_padding = 2*padding
        x_padding = padding
        thickness = 1.0
        stitch_height = 2.0

        # Check if pattern contains only knit stitches
        non_knit_indices = np.where(self.pattern != 0)
        if len(non_knit_indices[0]) > 0:
            row, col = non_knit_indices[0][0], non_knit_indices[1][0]
            stitch_name = self.STITCH_ORDER[self.pattern[row, col]]
            raise NotImplementedError(
                f"Rendering for stitch type '{stitch_name}' is not yet implemented. "
                f"Only knit stitches ('K') are currently supported.")

        # Calculate figure dimensions
        rows, cols = self.rows, self.cols

        # Create figure and axes if not provided
        if ax is None:
            # Calculate figsize based on chart dimensions if not provided
            if figsize is None:
                # Use golden ratio for default aspect ratio
                width = cols
                height = rows + stitch_height
                aspect_ratio = width / height
                figsize = (8, 8 / aspect_ratio)

            fig, ax = plt.subplots(figsize=figsize)
        else:
            # Use the provided axes
            fig = ax.figure

        # Set outline properties
        edgecolor = 'black' if show_outlines else 'none'
        linewidth = 0.5 if show_outlines else 0

        # Render stitches from bottom to top
        for i in range(rows):
            actual_row = rows - 1 - i  # Convert to actual row in the chart
            y_offset = i

            for j in range(cols):
                # Get stitch color
                color_index = self.color_indices[actual_row, j]
                rgb = self.color_palette.get_color_by_index(color_index)
                normalized_rgb = [c / 255 for c in rgb]

                # Stitch coordinates (in grid units)
                # Left leg of stitch
                left_leg = [
                    # Bottom right corner
                    [j + 0.5 - x_padding, y_offset + y_padding],
                    # Bottom right corner + thinness
                    [j + 0.5 - x_padding, y_offset + thickness - y_padding],
                    [j + x_padding, y_offset + stitch_height -
                        y_padding],  # Top left corner
                    # Top left corner - thinness
                    [j + x_padding, y_offset + stitch_height - thickness + y_padding],
                ]

                # Right leg of stitch
                right_leg = [
                    [j + 0.5 + x_padding, y_offset + y_padding],
                    [j + 0.5 + x_padding, y_offset + thickness - y_padding],
                    [j + 1 - x_padding, y_offset + stitch_height - y_padding],
                    [j + 1 - x_padding, y_offset +
                        stitch_height - thickness + y_padding],
                ]

                # Render the stitch legs
                left_patch = patches.Polygon(left_leg, closed=True, facecolor=normalized_rgb,
                                             edgecolor=edgecolor, linewidth=linewidth,
                                             zorder=i*2)
                right_patch = patches.Polygon(right_leg, closed=True, facecolor=normalized_rgb,
                                              edgecolor=edgecolor, linewidth=linewidth,
                                              zorder=i*2)
                ax.add_patch(left_patch)
                ax.add_patch(right_patch)

        # Set axis limits with a small margin
        margin = 0.05
        ax.set_xlim(-margin, cols + margin)
        ax.set_ylim(-margin, rows + stitch_height + margin)

        ax.set_aspect(ratio)
        ax.axis('off')

        plt.tight_layout()
        return fig

    def get_stitch(self, row, col):
        """
        Get the stitch type and color at the specified position.

        Parameters:
        -----------
        row : int
            Row index
        col : int
            Column index

        Returns:
        --------
        tuple
            (stitch_type, color_rgb) where stitch_type is the stitch name (string)
            and color_rgb is a tuple of (r, g, b) values
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            stitch_idx = self.pattern[row, col]
            stitch_type = self.STITCH_ORDER[stitch_idx] if 0 <= stitch_idx < len(
                self.STITCH_ORDER) else 'Unknown'

            color_idx = self.color_indices[row, col]
            color_rgb = self.color_palette.get_color_by_index(color_idx)

            return stitch_type, color_rgb
        else:
            raise IndexError(
                f"Position ({row, col}) is out of bounds for chart of size {self.rows}x{self.cols}")

    def set_stitch(self, row, col, stitch_type=None, color_rgb=None):
        """
        Set the stitch type and/or color at the specified position.

        Parameters:
        -----------
        row : int
            Row index
        col : int
            Column index
        stitch_type : str, optional
            Stitch type name (e.g., 'K', 'P', 'YO', etc.)
        color_rgb : tuple, optional
            RGB color tuple (r, g, b)

        Returns:
        --------
        bool
            True if the operation was successful
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise IndexError(
                f"Position ({row}, {col}) is out of bounds for chart of size {self.rows}x{self.cols}")

        # Store the original color index for later cleanup check
        original_color_idx = self.color_indices[row, col]

        # Update stitch type if provided
        if stitch_type is not None:
            stitch_idx = self.stitch_to_index(stitch_type)
            if stitch_idx != -1:
                self.pattern[row, col] = stitch_idx
            else:
                raise ValueError(f"Unknown stitch type: {stitch_type}")

        # Update color if provided
        if color_rgb is not None:
            color_rgb = tuple(int(c)
                              for c in color_rgb)  # Ensure integer values

            # Check if this color already exists in the palette
            color_idx = self.color_palette.get_index_by_color(color_rgb)

            if color_idx is None or color_idx == -1:
                # Need to add the color to the palette
                if hasattr(self.color_palette, 'add_color'):
                    # Use the add_color method if available
                    color_idx = self.color_palette.add_color(color_rgb)
                else:
                    # Create a new palette with the additional color
                    unique_colors = [self.color_palette.get_color_by_index(i)
                                     for i in range(self.color_palette.num_colors)]
                    unique_colors.append(color_rgb)
                    self.color_palette = KnittingColorPalette(unique_colors)
                    color_idx = self.color_palette.num_colors - 1

            # Update the color index for this position
            if color_idx is not None:
                self.color_indices[row, col] = color_idx

                # If we've changed to a different color, check if the original color is still used
                if original_color_idx != color_idx:
                    # Check if the original color is still used elsewhere
                    if not np.any(self.color_indices == original_color_idx):
                        # Original color is no longer used, optimize the palette
                        self.optimize_color_palette()

        return True

    def optimize_color_palette(self):
        """
        Remove unused colors from the palette and update color indices accordingly.
        This ensures the palette stays as small as possible.

        Returns:
        --------
        bool
            True if any colors were removed, False otherwise
        """
        # Find which color indices are actually used in the chart
        used_indices = np.unique(self.color_indices)

        # If all colors are used, no optimization needed
        if len(used_indices) == self.color_palette.num_colors:
            return False

        # Create a list of the colors that are actually used
        used_colors = [self.color_palette.get_color_by_index(
            idx) for idx in used_indices]

        # Map from current indices to new indices
        index_mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(
            used_indices)}

        # Create a new color palette with just the used colors
        new_palette = KnittingColorPalette(used_colors)

        # Update all indices in the chart using the mapping
        new_indices = np.zeros_like(self.color_indices)
        for i in range(self.rows):
            for j in range(self.cols):
                new_indices[i, j] = index_mapping[self.color_indices[i, j]]

        # Update the chart's color indices and palette
        self.color_indices = new_indices
        self.color_palette = new_palette

        return True

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
            json.dump(self.to_dict(), f, cls=KnittingChartJSONEncoder)

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
