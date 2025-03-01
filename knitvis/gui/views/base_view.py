from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal

from knitvis.chart import KnittingChart
from knitvis.gui.widgets.chart_navigation import ChartNavigationWidget


class BaseChartView(QWidget):
    """Base class for all chart visualization views"""

    # Signals for interaction
    stitch_clicked = pyqtSignal(int, int)  # Row, column

    def __init__(self, chart=None):
        super().__init__()
        self.chart = chart
        # Use grid layout instead of vertical layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Initialize default settings BEFORE calling init_ui
        self.settings = {
            'show_row_numbers': True,
            'show_col_numbers': True,
            'default_row_zoom': 20,
            'default_col_zoom': 20
        }

        # Create navigation widget which will contain the chart view
        self.navigation = ChartNavigationWidget()
        self.navigation.viewportChanged.connect(self.on_viewport_changed)

        # The navigation widget is now the main container
        self.layout.addWidget(self.navigation, 0, 0)

        # Initialize the UI (specific to each view)
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
        self.update_navigation_limits()
        self.update_view()

    def update_navigation_limits(self):
        """Update navigation limits based on chart dimensions"""
        if self.chart:
            self.navigation.update_navigation_limits(
                self.chart.rows, self.chart.cols)

    def on_viewport_changed(self, row, col, row_zoom, col_zoom):
        """Handle viewport parameter changes from navigation widget"""
        self.update_view()

    def get_viewport_parameters(self):
        """Get the current viewport parameters (row, col, row_zoom, col_zoom)"""
        return (
            self.navigation.row_pos.value(),
            self.navigation.col_pos.value(),
            self.navigation.row_zoom_slider.value(),
            self.navigation.col_zoom_slider.value()
        )

    def get_view_type(self):
        """Return the view type for settings (implemented by subclasses)"""
        return 'base'

    def apply_settings(self, settings):
        """Apply new settings to the view"""
        self.settings.update(settings)
        self.update_view()
