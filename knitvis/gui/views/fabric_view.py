import os

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
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QPoint


class FabricView(BaseChartView):
    """Knitting fabric visualization showing V-shaped stitches with navigation"""

    STITCHES_SHAPES = {
        0: np.array([
            [0, 0.8],
            [0.5, -0.2],
            [0.5, -1.2],
            [0, -0.2],
            [-0.5, -1.2],
            [-0.5, -0.2]
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

        # Initialize background image handling
        self.background_image = None

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

        # Initialize selection markers
        self.selection_markers = []

        # Connect click events with modifiers
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

    def get_view_type(self):
        """Return the view type for settings"""
        return 'fabric'

    def update_view(self):
        """Update the entire view (expensive operation)"""
        if not self.chart:
            return

        # Update navigation limits first
        self.update_navigation_limits()

        # Clear the figure
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        # Clear selection markers list since we're rebuilding everything
        self.selection_markers = []

        # Get parameters from settings
        show_outlines = self.settings.get('show_outlines', False)
        row_spacing = self.settings.get('row_spacing', 0.7)
        padding = self.settings.get('padding', 0.01)
        opacity = self.settings.get('opacity', 1.0)  # Get opacity setting
        show_row_numbers = self.settings.get('show_row_numbers', True)
        show_col_numbers = self.settings.get('show_col_numbers', True)
        x_axis_ticks_every_n = self.settings.get('x_axis_ticks_every_n', 1)
        y_axis_ticks_every_n = self.settings.get('y_axis_ticks_every_n', 1)
        x_axis_ticks_numbers_every_n_tics = self.settings.get(
            'x_axis_ticks_numbers_every_n_tics', 1)
        y_axis_ticks_numbers_every_n_ticks = self.settings.get(
            'y_axis_ticks_numbers_every_n_ticks', 1)

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
            # Define the chart range based on viewport
            chart_range = ((start_row, start_row + viewport_rows),
                           (start_col, start_col + viewport_cols))

            # Render the background image first (below the fabric)
            self.render_background(chart_range)

            # Call chart's render_fabric method without background image
            self.chart.render_fabric(
                fig=self.figure,
                ax=self.ax,
                chart_range=chart_range,
                ratio=row_spacing,
                padding=padding,
                show_outlines=show_outlines,
                opacity=opacity,
                x_axis_ticks_every_n=x_axis_ticks_every_n if show_col_numbers else 0,
                y_axis_ticks_every_n=y_axis_ticks_every_n if show_row_numbers else 0,
                x_axis_ticks_numbers_every_n_tics=x_axis_ticks_numbers_every_n_tics,
                y_axis_ticks_numbers_every_n_ticks=y_axis_ticks_numbers_every_n_ticks
            )

            # Draw the base chart to the canvas
            self.canvas.draw()

            # Cache the background AFTER drawing but BEFORE adding markers
            self.cache_background()

            # After drawing the fabric, add selection markers if needed
            if self.selected_stitches:
                self.draw_selection_markers()

        except Exception as e:
            # If chart contains non-knit stitches or other error, show a message
            self.ax.text(0.5, 0.5, f"Error rendering fabric: {str(e)}",
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12)
            self.ax.set_axis_off()
            self.canvas.draw()

    def render_background(self, chart_range):
        """Render background image for the fabric view"""
        # Only proceed if background is enabled and we have an image
        if not self.settings.get('background_image_enabled', False):
            return

        if self.background_image is None:
            image_path = self.settings.get('background_image_path', '')
            if (image_path and os.path.exists(image_path)):
                self.load_background_image(image_path)
            else:
                return

        # Get background opacity setting
        background_opacity = self.settings.get('background_image_opacity', 0.3)

        try:
            # Extract the viewport range
            range_row, range_col = chart_range

            # For fabric view, we need to adjust the extent slightly
            # to account for the different coordinate system
            img_extent = [
                0.5,                  # Left edge
                self.chart.cols+0.5,  # Right edge
                self.chart.rows+0.5,  # Bottom edge (y-axis is inverted)
                0.5                   # Top edge
            ]

            # Use imshow to display the background image covering the whole fabric area
            self.ax.imshow(
                self.background_image,
                extent=img_extent,
                aspect='auto',      # Allow stretching to fit
                alpha=background_opacity,
                zorder=1            # Below the stitches
            )

            # Set axis limits to match the current viewport
            self.ax.set_xlim(range_col[0], range_col[1] + 1)
            self.ax.set_ylim(range_row[1] + 1, range_row[0])

            print(
                f"Fabric background image displayed with extent {img_extent}")

        except Exception as e:
            print(f"Error rendering background image: {e}")

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

        # Check if click is within the chart area
        if start_row <= x <= end_row and start_col <= y <= end_col:
            try:
                expected_row = round(x)
                expected_col = round(y)

                test_positions = [
                    (expected_row, expected_col),
                    (expected_row, expected_col+1),
                    (expected_row, expected_col-1),
                    (expected_row+1, expected_col),
                    (expected_row-1, expected_col),
                ]

                # Find the stitch that was clicked
                for row, col in test_positions:
                    # Check if within viewport and valid chart coordinates
                    if row-1 < start_row or row-1 >= end_row or col-1 < start_col or col-1 >= end_col:
                        continue

                    # Check if stitch type is valid
                    stitch_type = self.chart.pattern[col-1, row-1]
                    if stitch_type not in self.STITCHES_SHAPES:
                        continue

                    # Check if click is inside the stitch shape
                    shape = self.STITCHES_SHAPES[stitch_type]
                    if self.is_point_inside_polygon(x-row, y-col, shape):
                        # Found the clicked stitch
                        chart_row, chart_col = col-1, row-1
                        print(
                            f"Clicked on stitch at chart coordinates ({chart_row}, {chart_col})")
                        self.handle_click(event, chart_row, chart_col)
                        return

                print("Click didn't hit any stitch precisely")

            except Exception as e:
                print(f"Error processing click: {e}")
        else:
            print("Click outside chart area")

    def draw_selection_markers(self):
        """Draw markers for selected stitches using their stitch shapes"""
        # Remove any existing selection markers
        for marker in self.selection_markers:
            try:
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

        # Collect all vertices for selected stitches
        patches = []
        for row, col in self.selected_stitches:
            # Skip if outside current viewport
            if not (start_row <= row < end_row and start_col <= col < end_col):
                continue

            # Get stitch type and check if it has a defined shape
            stitch_type = self.chart.pattern[row, col]
            if stitch_type not in self.STITCHES_SHAPES:
                continue

            # Get the base shape for this stitch type
            base_shape = self.STITCHES_SHAPES[stitch_type]

            # For each point in the shape, create a translated version for this stitch
            translated_shape = base_shape + np.array([col+1, row+1])
            # Add as a single polygon to patches
            patches.append(translated_shape)

        # If we have patches to draw, create a collection
        if patches:
            collection = plt.matplotlib.collections.PolyCollection(
                patches,
                facecolor='none',
                edgecolor='red',
                linewidth=2.0,
                alpha=0.8,
                zorder=10  # Ensure it's above everything
            )
            self.ax.add_collection(collection)
            self.selection_markers.append(collection)

            # Update the display
            if hasattr(self, 'canvas'):
                # If we have cached the background, restore it and just draw the markers
                if self._background is not None:
                    self.canvas.restore_region(self._background)
                    self.ax.draw_artist(collection)
                    self.canvas.blit(self.ax.bbox)
                else:
                    # Fall back to full redraw if no background is cached
                    self.canvas.draw()

    def show_context_menu(self, event, chart_row=None, chart_col=None):
        """Show context menu for single or multiple stitch operations"""
        # Note: The method signature now matches the base class expectation

        if not self.selected_stitches:
            # No stitches selected, nothing to do
            return

        # Create context menu
        menu = QMenu(self)

        # Menu actions
        if len(self.selected_stitches) == 1:
            # Single stitch actions
            row, col = self.selected_stitches[0]
            title_action = QAction(
                f"Stitch at Row {row+1}, Column {col+1}", self)
            title_action.setEnabled(False)
            menu.addAction(title_action)
            menu.addSeparator()

            edit_action = QAction("Edit Stitch...", self)
            edit_action.triggered.connect(lambda: self.edit_single_stitch())
            menu.addAction(edit_action)
        else:
            # Multiple stitch actions
            title_action = QAction(
                f"Edit {len(self.selected_stitches)} Stitches...", self)
            title_action.setEnabled(False)
            menu.addAction(title_action)
            menu.addSeparator()

            edit_action = QAction(
                f"Edit {len(self.selected_stitches)} Stitches...", self)
            edit_action.triggered.connect(
                lambda: self.edit_multiple_stitches())
            menu.addAction(edit_action)

        # Add Clear Selection action
        menu.addSeparator()
        clear_action = QAction("Clear Selection", self)
        clear_action.triggered.connect(self.clear_selection)
        menu.addAction(clear_action)

        # Show menu at cursor position or event position if provided
        if isinstance(event, QPoint):
            cursor_pos = event
        else:
            cursor_pos = self.mapFromGlobal(self.cursor().pos())

        menu.exec_(self.mapToGlobal(cursor_pos))

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

                # Provide warnings about aspect ratios
                chart_ratio = chart_cols / chart_rows
                fabric_ratio = chart_ratio * \
                    self.settings.get('row_spacing', 0.7)
                img_ratio = img_width / img_height
                if abs(fabric_ratio - img_ratio) > 0.1:
                    print(
                        f"Warning: Image aspect ratio ({img_ratio:.2f}) differs from fabric aspect ratio ({fabric_ratio:.2f})")
                    print("The background image may appear distorted")

            return True
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.background_image = None
            return False

    def showEvent(self, event):
        """Handle show event by updating the view if needed"""
        super().showEvent(event)
        # Update the view when the widget becomes visible
        self.update_view()
