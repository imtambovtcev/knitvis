import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
                             QSlider, QWidget, QPushButton, QSpinBox, QGridLayout, QFrame)
from PyQt5.QtCore import Qt

from knitvis.gui.views.base_view import BaseChartView


class FabricView(BaseChartView):
    """Knitting fabric visualization showing V-shaped stitches with navigation"""

    def init_ui(self):
        # Initialize additional view-specific settings 
        # Use setdefault to avoid errors if settings is None
        self.settings.setdefault('show_outlines', False)
        self.settings.setdefault('row_spacing', 0.7)
        
        # Create a container for the chart and its controls
        container = QFrame()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create figure for rendering
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        # Give canvas stretch factor
        container_layout.addWidget(self.canvas, 1)

        # Place the container inside the navigation widget's content area
        self.navigation.layout().itemAtPosition(0, 0).widget().setLayout(QVBoxLayout())
        self.navigation.layout().itemAtPosition(
            0, 0).widget().layout().addWidget(container)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

    def get_view_type(self):
        """Return the view type for settings"""
        return 'fabric'

    def update_view(self):
        if not self.chart:
            return

        # Update navigation limits first
        self.update_navigation_limits()

        # Clear the figure
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        # Get parameters from settings
        show_outlines = self.settings.get('show_outlines', False)
        # Direct value (no conversion needed)
        row_spacing = self.settings.get('row_spacing', 0.7)
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)

        # Store this for click handling calculations
        self.row_spacing = row_spacing

        # Get viewport parameters from the navigation widget
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate the end of the viewport
        rows, cols = self.chart.rows, self.chart.cols
        end_row = min(start_row + row_zoom, rows)
        end_col = min(start_col + col_zoom, cols)

        # Calculate actual viewport dimensions
        viewport_rows = end_row - start_row
        viewport_cols = end_col - start_col

        try:
            # Set viewport-specific parameters for fabric rendering
            self.render_fabric_viewport(
                start_row, start_col, viewport_rows, viewport_cols,
                row_spacing, show_outlines, show_row_numbers, show_col_numbers
            )

        except NotImplementedError as e:
            # If chart contains non-knit stitches, show a message
            self.ax.text(0.5, 0.5, str(e),
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12)
            self.ax.set_axis_off()

        self.canvas.draw()

    def render_fabric_viewport(self, start_row, start_col, viewport_rows, viewport_cols,
                               ratio, show_outlines, show_row_numbers, show_col_numbers):
        """Render only the specified viewport of the fabric"""
        # Derived parameters
        y_padding = 0.02  # Padding for stitch rendering
        x_padding = 0.01
        thickness = ratio
        stitch_height = thickness * 2

        # Check if any non-knit stitches in the viewport
        for i in range(start_row, start_row + viewport_rows):
            for j in range(start_col, start_col + viewport_cols):
                if self.chart.pattern[i, j] != 0:  # Not knit stitch
                    stitch_type, _ = self.chart.get_stitch(i, j)
                    raise NotImplementedError(
                        f"Rendering for stitch type '{stitch_type}' is not yet implemented. "
                        f"Only knit stitches ('K') are currently supported.")

        # Set outline properties
        edgecolor = 'black' if show_outlines else 'none'
        linewidth = 0.5 if show_outlines else 0

        # Render stitches from bottom to top
        for i in range(viewport_rows):
            actual_row = start_row + viewport_rows - 1 - \
                i  # Convert to actual row in the chart
            y_offset = i * ratio

            for j in range(viewport_cols):
                actual_col = start_col + j

                # Get stitch color
                color_index = self.chart.color_indices[actual_row, actual_col]
                rgb = self.chart.color_palette.get_color_by_index(color_index)
                normalized_rgb = [c / 255 for c in rgb]

                # Stitch coordinates (in grid units) - adjust for viewport
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
                self.ax.add_patch(left_patch)
                self.ax.add_patch(right_patch)

        # Set axis limits with a small margin
        margin = 0.05
        self.ax.set_xlim(-margin, viewport_cols + margin)
        self.ax.set_ylim(-margin, viewport_rows *
                         ratio + stitch_height + margin)

        # Add row and column numbers if enabled
        if show_row_numbers:
            for i in range(viewport_rows):
                # Row number on the left edge
                actual_row = start_row + i
                y_pos = viewport_rows * ratio - i * ratio
                self.ax.text(-0.5, y_pos, str(actual_row + 1),
                             ha='right', va='center', fontsize=8)

        if show_col_numbers:
            for j in range(viewport_cols):
                # Column number along the top edge
                actual_col = start_col + j
                self.ax.text(j + 0.5, -0.5, str(actual_col + 1),
                             ha='center', va='top', fontsize=8)

        self.ax.set_aspect('equal')
        self.ax.axis('off')

    def on_canvas_click(self, event):
        """Handle click events on the canvas and map to chart coordinates."""
        if event.xdata is None or event.ydata is None or not self.chart:
            return

        # Get viewport parameters from the navigation widget
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate the end of the viewport
        rows, cols = self.chart.rows, self.chart.cols
        end_row = min(start_row + row_zoom, rows)
        end_col = min(start_col + col_zoom, cols)
        viewport_rows = end_row - start_row

        # Calculate row and column from click coordinates
        x = event.xdata
        y = event.ydata

        # Column is the integer part of x, adjusted for viewport
        viewport_col = int(x)
        chart_col = start_col + viewport_col

        # Calculate row from y position (taking into account row_spacing)
        # Need to reverse the calculation since we render from bottom to top
        chart_row = start_row + viewport_rows - 1 - int(y / self.row_spacing)

        # Make sure coordinates are within chart bounds
        if 0 <= chart_row < rows and 0 <= chart_col < cols:
            print(
                f"Click at ({x:.2f}, {y:.2f}) -> Stitch at row {chart_row}, col {chart_col}")
            self.stitch_clicked.emit(chart_row, chart_col)
