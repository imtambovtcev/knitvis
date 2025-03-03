import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QAction, QMenu
from PyQt5.QtCore import Qt, QObject
from matplotlib.collections import PatchCollection, QuadMesh
from matplotlib.text import Text
import os

from knitvis.gui.views.base_view import BaseChartView
from knitvis.gui.dialogs.background_image_dialog import BackgroundImageDialog


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

        # Initialize background image handling
        self.background_image = None
        self.settings.setdefault('background_image_enabled', False)
        self.settings.setdefault('background_image_path', '')
        self.settings.setdefault('background_image_opacity', 0.3)

        # Add context menu for background image settings
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """Show context menu when right-clicking on the chart"""
        context_menu = QMenu(self)

        # Create menu actions
        bg_action = QAction("Configure Background Image...", self)
        bg_action.triggered.connect(self.configure_background)
        context_menu.addAction(bg_action)

        # Show menu at cursor position
        context_menu.exec_(self.canvas.mapToGlobal(pos))

    def configure_background(self):
        """Open dialog to configure background image settings"""
        dialog = BackgroundImageDialog(self, {
            'background_image_enabled': self.settings.get('background_image_enabled', False),
            'background_image_path': self.settings.get('background_image_path', ''),
            'background_image_opacity': self.settings.get('background_image_opacity', 0.3),
        })

        dialog.settingsApplied.connect(self.apply_background_settings)

        if dialog.exec_():
            # Dialog accepted (OK clicked)
            pass

    def apply_background_settings(self, settings):
        """Apply background image settings and update the view"""
        self.settings.update(settings)

        # If background is enabled, try to load the image
        if settings['background_image_enabled'] and settings['background_image_path']:
            self.load_background_image(settings['background_image_path'])
        else:
            self.background_image = None

        # Update the chart view
        self.update_view()

    def load_background_image(self, image_path):
        """Load a background image from file"""
        try:
            if not image_path or not os.path.exists(image_path):
                self.background_image = None
                return False

            # Load the image using matplotlib's imread
            self.background_image = plt.imread(image_path)

            # Print image info for debugging
            print(f"Loaded background image: {image_path}")
            print(
                f"Image shape: {self.background_image.shape}, dtype: {self.background_image.dtype}")

            # Check if image dimensions match chart dimensions for better alignment
            if self.chart:
                img_height, img_width = self.background_image.shape[:2]
                chart_rows, chart_cols = self.chart.rows, self.chart.cols
                print(
                    f"Chart dimensions: {chart_rows} rows x {chart_cols} columns")
                print(
                    f"Image dimensions: {img_height} height x {img_width} width")

                # Warn if aspect ratios don't match
                chart_ratio = chart_cols / chart_rows
                img_ratio = img_width / img_height
                if abs(chart_ratio - img_ratio) > 0.1:
                    print(
                        f"Warning: Image aspect ratio ({img_ratio:.2f}) differs from chart aspect ratio ({chart_ratio:.2f})")
                    print("The background image may appear distorted")

            return True
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.background_image = None
            return False

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
        opacity = self.settings.get('opacity', 1.0)  # Get opacity setting
        x_axis_ticks_every_n = self.settings.get('x_axis_ticks_every_n', 1)
        y_axis_ticks_every_n = self.settings.get('y_axis_ticks_every_n', 1)
        x_axis_ticks_numbers_every_n_tics = self.settings.get(
            'x_axis_ticks_numbers_every_n_tics', 1)
        y_axis_ticks_numbers_every_n_ticks = self.settings.get(
            'y_axis_ticks_numbers_every_n_ticks', 1)

        # Background image settings
        background_image = None
        background_opacity = self.settings.get('background_image_opacity', 0.3)

        # Check if background image is enabled and load if needed
        if self.settings.get('background_image_enabled', False):
            # Ensure the image is loaded
            if self.background_image is None:
                image_path = self.settings.get('background_image_path', '')
                if image_path and os.path.exists(image_path):
                    self.load_background_image(image_path)

            # Set background_image to the loaded image
            background_image = self.background_image

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
            show_borderline=cell_border,
            opacity=opacity,
            background_image=background_image,
            background_opacity=background_opacity,
            x_axis_ticks_every_n=x_axis_ticks_every_n if show_col_numbers else 0,
            y_axis_ticks_every_n=y_axis_ticks_every_n if show_row_numbers else 0,
            x_axis_ticks_numbers_every_n_tics=x_axis_ticks_numbers_every_n_tics,
            y_axis_ticks_numbers_every_n_ticks=y_axis_ticks_numbers_every_n_ticks
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
