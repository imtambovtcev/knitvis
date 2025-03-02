import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from matplotlib.collections import PatchCollection, QuadMesh
from matplotlib.text import Text

from knitvis.gui.views.base_view import BaseChartView


class ChartView(BaseChartView):
    """Traditional grid-based knitting chart visualization with navigation"""

    def init_ui(self):
        # Initialize additional view-specific settings
        self.settings.setdefault('cell_border', True)
        self.settings.setdefault('symbol_size', 12)

        # Create figure with tight layout
        self.figure = plt.figure(constrained_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # Allow figure to expand with window
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

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

        # Clear the axis and cache
        self.ax.clear()
        self.clear_cache()

        # Get display settings
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)
        cell_border = self.settings.get('cell_border', True)
        symbol_size = self.settings.get('symbol_size', 12)

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

        # Get viewport parameters
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate viewport dimensions
        viewport_rows = min(row_zoom, self.chart.rows - start_row)
        viewport_cols = min(col_zoom, self.chart.cols - start_col)

        # Draw cells and symbols efficiently
        rects = []
        texts = []

        # Create patches for each cell
        for i in range(viewport_rows):
            for j in range(viewport_cols):
                chart_i = start_row + i
                chart_j = start_col + j

                stitch_type, color_rgb = self.chart.get_stitch(
                    chart_i, chart_j)

                # Create rectangle for the cell
                rect = patches.Rectangle(
                    (j, viewport_rows - 1 - i), 1, 1,
                    facecolor=[c/255 for c in color_rgb],
                    edgecolor='black' if cell_border else 'none',
                    linewidth=0.5 if cell_border else 0
                )
                rects.append(rect)

                # Determine symbol and color
                symbol = self.chart.STITCH_SYMBOLS.get(stitch_type, '?')
                luminance = 0.2126 * \
                    color_rgb[0] + 0.7152 * \
                    color_rgb[1] + 0.0722 * color_rgb[2]
                text_color = "white" if luminance < 128 else "black"

                # Add text for symbol
                text = self.ax.text(
                    j + 0.5, viewport_rows - 1 - i + 0.5, symbol,
                    ha='center', va='center',
                    fontsize=symbol_size,
                    fontweight='bold',
                    color=text_color
                )
                texts.append(text)

        # Add cell patches efficiently as a collection
        cell_collection = PatchCollection(rects, match_original=True)
        self.ax.add_collection(cell_collection)

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

        # Cache the static background
        self.cache_background()

        # Draw everything
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
