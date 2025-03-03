class BaseController:
    """Base controller for processing view events"""

    def __init__(self, view, chart):
        self.view = view
        self.chart = chart
        self.connect_signals()

    def connect_signals(self):
        """Connect view signals to controller methods - implemented by subclasses"""
        pass

    def update_chart(self):
        """Update the view with the current chart data"""
        self.view.update_view()
