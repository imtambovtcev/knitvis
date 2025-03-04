import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt
from .chart import KnittingChart  # Use the updated chart class
from .palette import KnittingColorPalette


class DoubleKnittingCanvas:
    def __init__(self, front_pattern, back_pattern=None, front_color=(255, 255, 255), back_color=(0, 0, 0)):
        """
        Initialize canvas with front pattern and natural colors for each side.

        Args:
            front_pattern: Boolean numpy array for front pattern
            back_pattern: Optional boolean numpy array for back pattern (default is inverted front pattern)
            front_color: RGB tuple for the front side yarn color
            back_color: RGB tuple for the back side yarn color
        """
        self.front = front_pattern
        self.back = back_pattern if back_pattern is not None else ~front_pattern
        self.front_color = np.array(front_color, dtype=int)
        self.back_color = np.array(back_color, dtype=int)

        self._build_charts()

    def _build_charts(self):
        """Internal method to construct KnittingChart instances."""
        height, width = self.front.shape

        # Define stitch pattern:
        # Front uses knit (K), Back uses purl (P)
        front_stitches = np.full(
            (height, width), KnittingChart.stitch_to_index('K'), dtype=int)
        back_stitches = np.full(
            (height, width), KnittingChart.stitch_to_index('P'), dtype=int)

        # Generate color arrays
        front_colors = np.where(
            self.front[..., None], self.front_color, self.back_color)
        back_colors = np.where(
            self.back[..., None], self.front_color, self.back_color)

        # Create KnittingCharts for visualization
        self.front_chart = KnittingChart(front_stitches, front_colors)
        self.back_chart = KnittingChart(back_stitches, back_colors)

    @classmethod
    def from_pattern(cls, pattern: np.ndarray, target_size: tuple | None = None,
                     front_color=(255, 255, 255), back_color=(0, 0, 0)):
        """
        Create a canvas by interpolating the pattern to target size.

        True in pattern means front_color on front side, back_color on back side.
        False means back_color on front side, front_color on back side.
        """
        if not isinstance(pattern, np.ndarray) or pattern.dtype != bool:
            raise ValueError("Pattern must be a boolean numpy array")

        if target_size is None:
            return cls(pattern, front_color=front_color, back_color=back_color)

        # Calculate zoom factors
        zoom_y = target_size[0] / pattern.shape[0]
        zoom_x = target_size[1] / pattern.shape[1]

        interpolated = zoom(pattern, (zoom_y, zoom_x), order=0, mode='nearest')
        interpolated = interpolated > 0.5

        return cls(interpolated, front_color=front_color, back_color=back_color)

    @property
    def shape(self):
        """Return the shape of the canvas."""
        return self.front.shape

    def display(self):
        """Displays the front and back knitting charts."""
        fig1 = self.front_chart.display_chart()
        fig2 = self.back_chart.display_chart()

        return fig1, fig2

    def create_knitting_pattern(self):
        """
        Creates a double knitting pattern by interleaving front and back stitches.
        The pattern uses the same color logic: True = front_color, False = back_color.
        """
        height, width = self.shape
        pattern = np.zeros((height, width * 2), dtype=int)

        # Interleave front and back pattern
        pattern[:, ::2] = self.front_chart.pattern  # Front stitches
        pattern[:, 1::2] = self.back_chart.pattern  # Back stitches

        return pattern

    def get_knitting_chart(self):
        pattern = self.create_knitting_pattern()

        # Expand colors for visualization
        front_colors = self.front_chart.get_colors_rgb()
        back_colors = self.back_chart.get_colors_rgb()

        # Interleave color data
        height, width, _ = front_colors.shape
        interleaved_colors = np.zeros((height, width * 2, 3), dtype=int)
        interleaved_colors[:, ::2] = front_colors
        interleaved_colors[:, 1::2] = back_colors

        return KnittingChart(pattern, colors=interleaved_colors)

    def display_knitting_pattern(self):
        """Displays the double knitting pattern using a KnittingChart."""

        knitting_chart = self.get_knitting_chart()
        return knitting_chart.display_chart()

    def plot_full_pattern(self, rows_per_plot=10, figsize=(15, 3)):
        """
        Plots the full knitting pattern row by row.

        Args:
            rows_per_plot: Number of rows to show in each plot
            figsize: Figure size for each plot (width, height)
        """
        pattern = self.create_knitting_pattern()
        total_rows = pattern.shape[0]

        # Expand colors for visualization
        front_colors = self.front_chart.get_colors_rgb()
        back_colors = self.back_chart.get_colors_rgb()

        # Interleave colors
        height, width, _ = front_colors.shape
        interleaved_colors = np.zeros((height, width * 2, 3), dtype=int)
        interleaved_colors[:, ::2] = front_colors
        interleaved_colors[:, 1::2] = back_colors

        figs = []
        for i in range(0, total_rows, rows_per_plot):
            end_row = min(i + rows_per_plot, total_rows)
            sub_pattern = pattern[i:end_row]
            sub_colors = interleaved_colors[i:end_row]

            # Create chart for subset
            sub_chart = KnittingChart(sub_pattern, sub_colors)
            fig = sub_chart.display_chart()
            figs.append(fig)

        return figs
