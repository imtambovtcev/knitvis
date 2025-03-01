import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from knitvis.gui.views.base_view import BaseChartView


class ChartView(BaseChartView):
    """Traditional grid-based knitting chart visualization with navigation"""

    def init_ui(self):
        # Initialize additional view-specific settings
        # Use setdefault to avoid errors if settings is None
        self.settings.setdefault('cell_border', True)
        self.settings.setdefault('symbol_size', 12)
        
        # Chart display
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Place the canvas inside the content area of the navigation widget
        self.navigation.layout().itemAtPosition(0, 0).widget().setLayout(QVBoxLayout())
        self.navigation.layout().itemAtPosition(
            0, 0).widget().layout().addWidget(self.canvas)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

    def get_view_type(self):
        """Return the view type for settings"""
        return 'chart'

    def update_view(self):
        if not self.chart:
            return

        # Update navigation limits first
        self.update_navigation_limits()

        # Clear the axis
        self.ax.clear()

        # Get the viewport parameters from the navigation widget
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate end positions, ensuring we don't go beyond chart boundaries
        rows, cols = self.chart.rows, self.chart.cols
        end_row = min(start_row + row_zoom, rows)
        end_col = min(start_col + col_zoom, cols)

        # Calculate actual viewport dimensions
        viewport_rows = end_row - start_row
        viewport_cols = end_col - start_col

        # Get display settings
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)
        cell_border = self.settings.get('cell_border', True)
        symbol_size = self.settings.get('symbol_size', 12)

        # Draw the visible portion of the chart
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                # Get stitch info using get_stitch method
                stitch_type, color_rgb = self.chart.get_stitch(i, j)

                # Get the symbol for this stitch type
                symbol = self.chart.STITCH_SYMBOLS.get(stitch_type, '?')

                # Normalize RGB to 0-1 range for Matplotlib
                normalized_rgb = [c / 255 for c in color_rgb]

                # Calculate relative luminance to determine text color
                luminance = 0.2126 * \
                    color_rgb[0] + 0.7152 * \
                    color_rgb[1] + 0.0722 * color_rgb[2]
                text_color = "black" if luminance > 128 else "white"

                # Convert chart coordinates to viewport coordinates
                viewport_i = i - start_row
                viewport_j = j - start_col

                # Draw the cell rectangle (invert the y-axis for display)
                # Fix: Set facecolor and edgecolor separately instead of using color
                edgecolor = 'black' if cell_border else 'none'
                rect = patches.Rectangle((viewport_j, viewport_rows - 1 - viewport_i),
                                         1, 1, facecolor=normalized_rgb, edgecolor=edgecolor,
                                         linewidth=0.5 if cell_border else 0)
                self.ax.add_patch(rect)

                # Draw the stitch symbol with appropriate text color
                self.ax.text(viewport_j + 0.5, viewport_rows - 1 - viewport_i + 0.5, symbol,
                             ha='center', va='center', fontsize=symbol_size, fontweight='bold',
                             color=text_color)

        # Set axis limits and appearance
        self.ax.set_xlim(0, viewport_cols)
        self.ax.set_ylim(0, viewport_rows)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_frame_on(True)

        # Add row and column numbers if enabled
        if show_row_numbers:
            for i in range(viewport_rows):
                # Row number on the left edge
                actual_row = start_row + i
                self.ax.text(-0.2, viewport_rows - 1 - i + 0.5, str(actual_row + 1),
                             ha='center', va='center', fontsize=8)

        if show_col_numbers:
            for j in range(viewport_cols):
                # Column number along the top edge
                actual_col = start_col + j
                self.ax.text(j + 0.5, viewport_rows + 0.2, str(actual_col + 1),
                             ha='center', va='center', fontsize=8)

        # No title needed - viewport info is displayed in navigation widget

        # Redraw the canvas
        self.canvas.draw()

    def on_canvas_click(self, event):
        """Handle canvas click event by converting viewport coordinates to chart coordinates"""
        if event.xdata is None or event.ydata is None or not self.chart:
            return

        # Get viewport parameters
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate actual viewport dimensions
        rows, cols = self.chart.rows, self.chart.cols
        end_row = min(start_row + row_zoom, rows)
        end_col = min(start_col + col_zoom, cols)
        viewport_rows = end_row - start_row

        # Convert click coordinates (in viewport) to chart coordinates
        viewport_j = int(event.xdata)
        viewport_i = viewport_rows - 1 - int(event.ydata)

        chart_i = start_row + viewport_i
        chart_j = start_col + viewport_j

        # Verify coordinates are within bounds
        if 0 <= chart_i < rows and 0 <= chart_j < cols:
            self.stitch_clicked.emit(chart_i, chart_j)
