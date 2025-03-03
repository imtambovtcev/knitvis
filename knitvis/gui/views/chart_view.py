import os

import matplotlib.image as mpimg
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import PatchCollection, QuadMesh
from matplotlib.text import Text
from PyQt5.QtCore import QObject, QPoint, Qt
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QMenu, QSizePolicy,
                             QVBoxLayout, QWidget)

from knitvis.gui.dialogs import MultipleStitchDialog, StitchDialog
from knitvis.gui.dialogs.background_image_dialog import BackgroundImageDialog
from knitvis.gui.views.base_view import BaseChartView


class ChartView(BaseChartView):
    """Traditional grid-based knitting chart visualization with navigation"""

    def init_ui(self):
        # Initialize additional view-specific settings
        self.settings.setdefault('cell_border', True)
        # Remove the show_symbols setting, we'll just use symbol_size=0 to hide
        self.settings.setdefault('symbol_size', 12)

        # Create figure with tight layout
        self.figure = plt.figure(constrained_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # Add these lines to ensure the canvas can receive keyboard focus
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

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

        # Add canvas event handling for keyboard events
        self.canvas.mpl_connect('key_press_event', self.on_canvas_key_press)

        # Store selection visualization objects
        self.selection_markers = []

        # Initialize background image handling
        self.background_image = None
        self.settings.setdefault('background_image_enabled', False)
        self.settings.setdefault('background_image_path', '')
        self.settings.setdefault('background_image_opacity', 0.3)

        # Add context menu for background image settings
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos, chart_row=None, chart_col=None):
        """Show context menu when right-clicking on the chart"""
        # Check if it's a right-click on a stitch or a general context menu request
        if chart_row is not None and chart_col is not None:
            # This is from handle_click - delegate to the base class implementation
            super().show_context_menu(pos, chart_row, chart_col)
            return

        # This is from the customContextMenuRequested signal (general right-click)
        context_menu = QMenu(self)

        # Create menu actions
        bg_action = QAction("Configure Background Image...", self)
        bg_action.triggered.connect(self.configure_background)
        context_menu.addAction(bg_action)

        # If stitches are selected, add stitch-related options
        if self.selected_stitches:
            context_menu.addSeparator()

            if len(self.selected_stitches) == 1:
                row, col = self.selected_stitches[0]
                edit_action = QAction(
                    f"Edit Stitch at ({row+1}, {col+1})...", self)
                edit_action.triggered.connect(
                    lambda: self.edit_single_stitch())
                context_menu.addAction(edit_action)
            else:
                edit_action = QAction(
                    f"Edit {len(self.selected_stitches)} Selected Stitches...", self)
                edit_action.triggered.connect(
                    lambda: self.edit_multiple_stitches())
                context_menu.addAction(edit_action)

            # Add clear selection action
            clear_action = QAction("Clear Selection", self)
            clear_action.triggered.connect(self.clear_selection)
            context_menu.addAction(clear_action)

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
        """Update the entire view (expensive operation)"""
        if not self.chart:
            return

        # Update navigation limits first
        self.update_navigation_limits()

        # IMPORTANT: Clear *everything* first to avoid traces
        self.figure.clear()  # Clear the entire figure, not just the axis
        self.ax = self.figure.add_subplot(111)  # Create a fresh axis

        # Reset all state tracking
        self.clear_cache()
        self.selection_markers = []

        # Get viewport parameters
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate viewport dimensions
        viewport_rows = min(row_zoom, self.chart.rows - start_row)
        viewport_cols = min(col_zoom, self.chart.cols - start_col)

        # Get display settings
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)
        cell_border = self.settings.get('cell_border', True)
        # If size=0, no symbols will be shown
        symbol_size = self.settings.get('symbol_size', 12)
        opacity = self.settings.get('opacity', 1.0)
        x_axis_ticks_every_n = self.settings.get('x_axis_ticks_every_n', 1)
        y_axis_ticks_every_n = self.settings.get('y_axis_ticks_every_n', 1)
        x_axis_ticks_numbers_every_n_tics = self.settings.get(
            'x_axis_ticks_numbers_every_n_tics', 1)
        y_axis_ticks_numbers_every_n_ticks = self.settings.get(
            'y_axis_ticks_numbers_every_n_ticks', 1)

        # Define chart range based on viewport
        chart_range = ((start_row, start_row + viewport_rows),
                       (start_col, start_col + viewport_cols))

        # Render background image first (below the chart)
        self.render_background(chart_range)

        # Use display_chart method from KnittingChart to render the chart itself
        self.chart.display_chart(
            fig=self.figure,
            ax=self.ax,
            chart_range=chart_range,
            fontsize=symbol_size,  # If symbol_size=0, no symbols will be shown
            fontweight='bold',
            ratio=None,
            show_borderline=cell_border,
            opacity=opacity,
            x_axis_ticks_every_n=x_axis_ticks_every_n if show_col_numbers else 0,
            y_axis_ticks_every_n=y_axis_ticks_every_n if show_row_numbers else 0,
            x_axis_ticks_numbers_every_n_tics=x_axis_ticks_numbers_every_n_tics,
            y_axis_ticks_numbers_every_n_ticks=y_axis_ticks_numbers_every_n_ticks
        )

        # Draw everything before adding markers
        self.canvas.draw()

        # Only attempt to cache background AFTER drawing
        self.cache_background()

        # After drawing the chart, add selection markers if needed
        if self.selected_stitches:
            self.draw_selection_markers()

    def render_background(self, chart_range):
        """Render background image for the chart view"""
        # Only proceed if background is enabled and we have an image
        if not self.settings.get('background_image_enabled', False):
            return

        if self.background_image is None:
            image_path = self.settings.get('background_image_path', '')
            if image_path and os.path.exists(image_path):
                self.load_background_image(image_path)
            else:
                return

        # Get background opacity setting
        background_opacity = self.settings.get('background_image_opacity', 0.3)

        try:
            # Extract the viewport range
            range_row, range_col = chart_range

            # Set the extent to cover the entire chart area
            img_extent = [
                0.5,                # Left edge
                self.chart.cols+0.5,  # Right edge
                self.chart.rows+0.5,  # Bottom edge (y-axis is inverted)
                0.5                 # Top edge
            ]

            # Use imshow to display the background image covering the whole chart
            self.ax.imshow(
                self.background_image,
                extent=img_extent,
                aspect='auto',      # Allow stretching to fit
                alpha=background_opacity,
                zorder=1            # Below the stitches
            )

            # Set axis limits to match the current viewport
            self.ax.set_xlim(range_col[0] + 0.5, range_col[1] + 0.5)
            self.ax.set_ylim(range_row[1] + 0.5, range_row[0] + 0.5)

            print(f"Chart background image displayed with extent {img_extent}")

        except Exception as e:
            print(f"Error rendering background image: {e}")

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
            # Use base class method to handle the click
            self.handle_click(event, chart_i, chart_j)

    def on_canvas_key_press(self, event):
        """Handle key press events from matplotlib canvas"""
        print(f"Canvas key press event received: {event.key}")  # Debug print
        if event.key == 'escape':
            print("ESC pressed in canvas - Clearing selection")
            self.clear_selection()

    def draw_selection_markers(self):
        """Draw markers for selected stitches without redrawing the entire view"""
        # Make sure all previous markers are removed
        for marker in self.selection_markers:
            try:
                if marker in self.ax.patches:
                    marker.remove()
            except:
                pass

        self.selection_markers = []

        # Get viewport parameters
        start_row, start_col, row_zoom, col_zoom = self.get_viewport_parameters()

        # Calculate actual viewport dimensions
        rows, cols = self.chart.rows, self.chart.cols
        end_row = min(start_row + row_zoom, rows)
        end_col = min(start_col + col_zoom, cols)

        # Create new selection markers for visible selected stitches
        for row, col in self.selected_stitches:
            # Skip if outside current viewport
            if not (start_row <= row < end_row and start_col <= col < end_col):
                continue

            # For chart view, draw a highlight rectangle for the cell
            marker = patches.Rectangle(
                xy=(col + 0.5, row + 0.5),  # Bottom-left corner
                width=1.0,
                height=1.0,
                edgecolor='red',
                facecolor='none',
                linewidth=2.0,
                alpha=0.8,
                zorder=10  # Ensure it's above everything
            )
            self.ax.add_patch(marker)
            self.selection_markers.append(marker)

        # Only update the display if there are markers to show
        if self.selection_markers and hasattr(self, 'canvas'):
            self.canvas.draw()  # Just draw everything for reliability

    def edit_single_stitch(self):
        """Edit a single selected stitch"""
        if self.selected_stitches:
            row, col = self.selected_stitches[0]
            # Use the existing dialog and controller for single stitch editing
            self.stitch_clicked.emit(row, col)

    def edit_multiple_stitches(self):
        """Edit multiple selected stitches"""
        from knitvis.gui.dialogs import MultipleStitchDialog

        if not self.selected_stitches or not self.chart:
            return

        # Create dialog for bulk editing
        dialog = MultipleStitchDialog(self, self.chart, self.selected_stitches)

        if dialog.exec_():
            # Dialog accepted, get the selected values
            stitch_type, color = dialog.get_selection()

            # Apply changes to all selected stitches
            for row, col in self.selected_stitches:
                # Convert stitch index to name
                if stitch_type is not None:
                    stitch_name = self.chart.STITCH_ORDER[stitch_type]
                else:
                    stitch_name = None

                # Convert QColor to RGB tuple if needed
                if color and color.isValid():
                    color_rgb = (color.red(), color.green(), color.blue())
                else:
                    color_rgb = None

                # Update the stitch in the chart
                self.chart.set_stitch(
                    row, col, stitch_type=stitch_name, color_rgb=color_rgb)

            # Redraw chart with updated stitches
            self.update_view()

    def showEvent(self, event):
        """Handle show event by updating the view if needed"""
        super().showEvent(event)
        # Update the view when the widget becomes visible
        self.update_view()
