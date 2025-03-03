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

        # Get viewport parameters
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate viewport dimensions
        viewport_rows = min(row_zoom, self.chart.rows - start_row)
        viewport_cols = min(col_zoom, self.chart.cols - start_col)

        # Get display settings
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)
        cell_border = self.settings.get('cell_border', True)
        symbol_size = self.settings.get('symbol_size', 12)

        # Define chart range
        chart_range = ((start_row, start_row + viewport_rows),
                       (start_col, start_col + viewport_cols))

        # Use display_chart method from KnittingChart
        self.chart.display_chart(
            fig=self.figure,
            ax=self.ax,
            chart_range=chart_range,
            fontsize=symbol_size if symbol_size > 0 else 0,
            fontweight='bold',
            ratio=None,
            # show_outlines=cell_border,
            x_axis_ticks_every_n=1 if show_col_numbers else 0,
            y_axis_ticks_every_n=1 if show_row_numbers else 0,
            x_axis_ticks_numbers_every_n_tics=1,
            y_axis_ticks_numbers_every_n_ticks=1
        )

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
        viewport_j = int(event.xdata - 0.5)
        viewport_i = int(event.ydata - 0.5)

        chart_i = viewport_i
        chart_j = viewport_j

        # Verify coordinates are within bounds
        if 0 <= chart_i < rows and 0 <= chart_j < cols:
            self.stitch_clicked.emit(chart_i, chart_j)
