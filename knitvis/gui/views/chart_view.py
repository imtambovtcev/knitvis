import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from knitvis.gui.views.base_view import BaseChartView


class ChartView(BaseChartView):
    """Traditional grid-based knitting chart visualization"""

    def init_ui(self):
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

    def update_view(self):
        if not self.chart:
            return

        self.ax.clear()

        rows, cols = self.chart.rows, self.chart.cols

        for i in range(rows):
            for j in range(cols):
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

                # Draw the cell rectangle
                self.ax.add_patch(plt.Rectangle((j, rows - 1 - i), 1, 1,
                                                color=normalized_rgb, edgecolor='black'))

                # Draw the stitch symbol with appropriate text color
                self.ax.text(j + 0.5, rows - 1 - i + 0.5, symbol,
                             ha='center', va='center', fontsize=12, fontweight='bold',
                             color=text_color)

        self.ax.set_xlim(0, cols)
        self.ax.set_ylim(0, rows)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_frame_on(False)

        self.canvas.draw()

    def on_canvas_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        j = int(event.xdata)
        i = self.chart.rows - 1 - int(event.ydata)

        if 0 <= i < self.chart.rows and 0 <= j < self.chart.cols:
            self.stitch_clicked.emit(i, j)
