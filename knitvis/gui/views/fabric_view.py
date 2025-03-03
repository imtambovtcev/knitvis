import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.path import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCheckBox, QFrame, QGridLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider, QSpinBox,
                             QVBoxLayout, QWidget)

from knitvis.gui.views.base_view import BaseChartView


class FabricView(BaseChartView):
    """Knitting fabric visualization showing V-shaped stitches with navigation"""

    STITCHES_SHAPES = {
        0: np.array([
            [0, 1],
            [0.5, 0],
            [0.5, -1],
            [0, 0],
            [-0.5, -1],
            [-0.5, 0]
        ]),
        1: np.array([
            [-0.5, 0.3],
            [-0.5, -0.3],
            [0.5, -0.3],
            [0.5, 0.3]
        ])
    }

    def init_ui(self):
        # Initialize additional view-specific settings
        # Use setdefault to avoid errors if settings is None
        self.settings.setdefault('show_outlines', False)
        self.settings.setdefault('row_spacing', 0.7)
        self.settings.setdefault('padding', 0.01)
        self.settings.setdefault('opacity', 1.0)  # Default opacity

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
        row_spacing = self.settings.get('row_spacing', 0.7)
        padding = self.settings.get('padding', 0.01)
        opacity = self.settings.get('opacity', 1.0)  # Get opacity setting
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)
        x_axis_ticks_every_n = self.settings.get('x_axis_ticks_every_n', 1)
        y_axis_ticks_every_n = self.settings.get('y_axis_ticks_every_n', 1)
        x_axis_ticks_numbers_every_n_tics = self.settings.get('x_axis_ticks_numbers_every_n_tics', 1)
        y_axis_ticks_numbers_every_n_ticks = self.settings.get('y_axis_ticks_numbers_every_n_ticks', 1)

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
            # Use render_fabric from KnittingChart instead of custom rendering
            chart_range = ((start_row, start_row + viewport_rows),
                           (start_col, start_col + viewport_cols))

            # Call chart's render_fabric method with our parameters
            self.chart.render_fabric(
                fig=self.figure,
                ax=self.ax,
                chart_range=chart_range,
                ratio=row_spacing,
                padding=padding,
                show_outlines=show_outlines,
                opacity=opacity,  # Pass opacity to render_fabric
                x_axis_ticks_every_n=x_axis_ticks_every_n if show_col_numbers else 0,
                y_axis_ticks_every_n=y_axis_ticks_every_n if show_row_numbers else 0,
                x_axis_ticks_numbers_every_n_tics=x_axis_ticks_numbers_every_n_tics,
                y_axis_ticks_numbers_every_n_ticks=y_axis_ticks_numbers_every_n_ticks
            )

        except Exception as e:
            # If chart contains non-knit stitches or other error, show a message
            self.ax.text(0.5, 0.5, f"Error rendering fabric: {str(e)}",
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12)
            self.ax.set_axis_off()

        self.canvas.draw()

    @staticmethod
    def is_point_inside_polygon(x, y, shape):
        """
        Determines if a point (x, y) is inside a polygon using Matplotlib's Path.
        """
        path = Path(shape)  # Create a polygon path
        return path.contains_point((x, y))

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

        # Calculate row and column from click coordinates
        x = event.xdata
        y = event.ydata

        print(f"Click at ({x}, {y})")
        print(f'{start_row = } {end_row = } {start_col = } {end_col = }')

        if start_row-1 < x < end_row+1 and start_col-1 < y < end_col+1:
            print("Click inside viewport")
            expected_row = round(x)
            expected_col = round(y)

            test_rows = [
                (expected_row, expected_col),
                (expected_row, expected_col+1),
                (expected_row, expected_col-1),
                (expected_row+1, expected_col),
                (expected_row-1, expected_col),]

            correct_index = None
            for row, col in test_rows:
                if not (start_row <= row-1 < end_row and start_col <= col-1 < end_col):
                    continue
                stitch_type = self.chart.pattern[col-1, row-1]
                if stitch_type not in self.STITCHES_SHAPES:
                    continue
                shape = self.STITCHES_SHAPES[stitch_type]
                if self.is_point_inside_polygon(x-row, y-col, shape):
                    correct_index = (row, col)
                    break

            if correct_index:
                print(f"Clicked on stitch at {correct_index}")
                correct_index = correct_index[1]-1, correct_index[0]-1
                self.stitch_clicked.emit(*correct_index)
            else:
                print("Clicked outside of any stitch")
