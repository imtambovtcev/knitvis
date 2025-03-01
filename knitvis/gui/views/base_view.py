from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

from knitvis.chart import KnittingChart


class BaseChartView(QWidget):
    """Base class for all chart visualization views"""

    # Signals for interaction
    stitch_clicked = pyqtSignal(int, int)  # Row, column

    def __init__(self, chart=None):
        super().__init__()
        self.chart = chart
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.init_ui()

        if chart:
            self.update_view()

    def init_ui(self):
        """Initialize the UI components - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement init_ui")

    def update_view(self):
        """Update the view with current chart data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement update_view")

    def set_chart(self, chart):
        """Set a new chart and update the view"""
        self.chart = chart
        self.update_view()
