import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
                             QSlider, QWidget, QPushButton, QSpinBox, QGridLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from matplotlib.collections import PolyCollection

from knitvis.gui.views.base_view import BaseChartView


class FabricView(BaseChartView):
    """Knitting fabric visualization showing V-shaped stitches with navigation"""

    def init_ui(self):
        # Initialize settings
        self.settings.setdefault('show_outlines', False)
        self.settings.setdefault('row_spacing', 0.7)

        # Create figure with tight layout
        self.figure = plt.figure(constrained_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # Allow figure to expand with window
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Create container with minimal margins
        container = QFrame()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.canvas)

        # Place in navigation widget
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

        # Get display settings
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)

        # Calculate margins based on whether numbers are shown
        left_margin = 0.05 if not show_row_numbers else 0.1
        bottom_margin = 0.05 if not show_col_numbers else 0.1
        right_margin = 0.02
        top_margin = 0.02

        # Adjust figure margins
        self.figure.subplots_adjust(
            left=left_margin,
            right=1.0 - right_margin,
            bottom=bottom_margin,
            top=1.0 - top_margin,
            wspace=0,
            hspace=0
        )

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
            # Check if chart contains non-knit stitches before rendering
            self.check_for_non_knit_stitches(
                start_row, start_col, viewport_rows, viewport_cols)

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

    def check_for_non_knit_stitches(self, start_row, start_col, viewport_rows, viewport_cols):
        """Check if any non-knit stitches in the viewport and raise an error if found"""
        for i in range(start_row, start_row + viewport_rows):
            for j in range(start_col, start_col + viewport_cols):
                if self.chart.pattern[i, j] != 0:  # Not knit stitch
                    stitch_type, _ = self.chart.get_stitch(i, j)
                    raise NotImplementedError(
                        f"Rendering for stitch type '{stitch_type}' is not yet implemented. "
                        f"Only knit stitches ('K') are currently supported.")

    def render_fabric_viewport(self, start_row, start_col, viewport_rows, viewport_cols,
                               ratio, show_outlines, show_row_numbers, show_col_numbers):
        """Optimized fabric rendering using polygon collections"""
        # Calculate parameters
        y_padding = 0.02
        x_padding = 0.01
        thickness = ratio
        stitch_height = thickness * 2

        # Pre-calculate all vertices and colors for left and right legs
        left_verts = []
        right_verts = []
        colors = []

        # Create vertices for all stitches at once
        for i in range(viewport_rows):
            actual_row = start_row + viewport_rows - 1 - i
            y_offset = i * ratio

            for j in range(viewport_cols):
                actual_col = start_col + j

                # Get color
                color_index = self.chart.color_indices[actual_row, actual_col]
                rgb = self.chart.color_palette.get_color_by_index(color_index)
                colors.append([c/255 for c in rgb])

                # Left leg vertices
                left_verts.append([
                    [j + 0.5 - x_padding, y_offset + y_padding],
                    [j + 0.5 - x_padding, y_offset + thickness - y_padding],
                    [j + x_padding, y_offset + stitch_height - y_padding],
                    [j + x_padding, y_offset + stitch_height - thickness + y_padding]
                ])

                # Right leg vertices
                right_verts.append([
                    [j + 0.5 + x_padding, y_offset + y_padding],
                    [j + 0.5 + x_padding, y_offset + thickness - y_padding],
                    [j + 1 - x_padding, y_offset + stitch_height - y_padding],
                    [j + 1 - x_padding, y_offset +
                        stitch_height - thickness + y_padding]
                ])

        # Create polygon collections for efficient rendering
        edge_color = 'black' if show_outlines else None
        line_width = 0.5 if show_outlines else 0

        left_collection = PolyCollection(
            left_verts, facecolors=colors, edgecolors=edge_color,
            linewidth=line_width, antialiased=True)
        right_collection = PolyCollection(
            right_verts, facecolors=colors, edgecolors=edge_color,
            linewidth=line_width, antialiased=True)

        # Add collections to axes
        self.ax.add_collection(left_collection)
        self.ax.add_collection(right_collection)

        # Set limits and appearance
        self.ax.set_xlim(-0.2, viewport_cols + 0.2)
        self.ax.set_ylim(-0.2, viewport_rows * ratio + stitch_height + 0.2)
        self.ax.set_aspect('equal')

        # Cache the result
        self.cache_background()

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
