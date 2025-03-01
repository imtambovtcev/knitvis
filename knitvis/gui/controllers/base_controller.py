class BaseController:
    """Base controller class for chart views"""

    def __init__(self, view, chart):
        self.view = view
        self.chart = chart

        # Connect view signals to controller methods
        self.connect_signals()

    def connect_signals(self):
        """Connect view signals to controller methods"""
        raise NotImplementedError("Subclasses must implement connect_signals")

    def update_chart(self):
        """Update the chart and refresh the view"""
        self.view.update_view()
