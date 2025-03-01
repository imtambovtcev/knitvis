import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QSlider, QLabel, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from knitvis.gui.views.base_view import BaseChartView


class FabricView(BaseChartView):
    """Knitting fabric visualization showing V-shaped stitches"""

    def init_ui(self):
        # Create controls for fabric visualization
        controls_layout = QHBoxLayout()

        # Show outlines checkbox
        self.outlines_checkbox = QCheckBox("Show Outlines")
        self.outlines_checkbox.setChecked(False)
        self.outlines_checkbox.toggled.connect(self.update_view)
        controls_layout.addWidget(self.outlines_checkbox)

        # Row spacing slider
        spacing_layout = QHBoxLayout()
        spacing_layout.addWidget(QLabel("Row Spacing:"))
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(1, 100)
        self.spacing_slider.setValue(70)  # Default value 0.7
        self.spacing_slider.valueChanged.connect(self.update_view)
        spacing_layout.addWidget(self.spacing_slider)
        controls_layout.addLayout(spacing_layout)

        # Create container for controls
        controls_container = QWidget()
        controls_container.setLayout(controls_layout)

        # Create figure for rendering
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setVisible(True)  # Explicitly set canvas to visible

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

        # Use the inherited layout instead of creating a new one
        self.layout.addWidget(controls_container)
        self.layout.addWidget(self.canvas, 1)

    def update_view(self):
        if not self.chart:
            return

        # Clear the figure
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        # Get parameters from controls
        show_outlines = self.outlines_checkbox.isChecked()
        row_spacing = self.spacing_slider.value() / 100.0  # Convert to 0.0-1.0 range

        # Store these for click handling calculations
        self.row_spacing = row_spacing
        self.stitch_height = row_spacing * 2  # Height of a stitch is 2x ratio

        try:
            # Try to render the fabric using current parameters
            self.chart.render_fabric(
                figsize=None,  # Let the method determine appropriate size
                ratio=row_spacing,
                padding=0.01,
                show_outlines=show_outlines,
                ax=self.ax  # Pass our existing axis
            )

            # Store limits for click handling
            self.x_min, self.x_max = self.ax.get_xlim()
            self.y_min, self.y_max = self.ax.get_ylim()

        except NotImplementedError as e:
            # If chart contains non-knit stitches, show a message
            self.ax.text(0.5, 0.5, str(e),
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12)
            self.ax.set_axis_off()

        self.canvas.draw()

    def on_canvas_click(self, event):
        """Handle click events on the canvas and map to chart coordinates."""
        if event.xdata is None or event.ydata is None or not self.chart:
            return

        rows, cols = self.chart.rows, self.chart.cols

        # Get the click coordinates
        x = event.xdata
        y = event.ydata

        # Column is more straightforward - just the integer part of x
        # But ensure it's within bounds
        col = int(x)
        if col < 0:
            col = 0
        elif col >= cols:
            col = cols - 1

        # For the row, we need to account for the V-shaped visualization
        # The fabric visualization starts from the bottom, with rows stacked vertically
        # Each row's y position is: row_number * row_spacing from the bottom

        # Calculate the approximate row
        # In fabric view, row 0 (chart bottom) is displayed at the top
        # The top of the chart (row rows-1) is at y=0
        # Each row takes up row_spacing height, with some overlap
        approx_row = int(y / self.row_spacing)

        # Adjust for the fact that row 0 is at the bottom of the chart
        # But displayed at the top of the visualization
        row = rows - 1 - approx_row

        # Ensure row is within bounds
        if row < 0:
            row = 0
        elif row >= rows:
            row = rows - 1

        # Debug print to see where we're clicking
        print(f"Click at ({x:.2f}, {y:.2f}) -> Stitch at row {row}, col {col}")

        # Emit the signal with the calculated row and column
        self.stitch_clicked.emit(row, col)
