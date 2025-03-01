from PyQt5.QtWidgets import QColorDialog, QMenu, QAction
from PyQt5.QtGui import QColor

from knitvis.gui.controllers.base_controller import BaseController
from knitvis.gui.dialogs import StitchDialog


class ChartController(BaseController):
    """Controller for chart view interactions"""

    def connect_signals(self):
        """Connect view signals to controller methods"""
        self.view.stitch_clicked.connect(self.on_stitch_clicked)

    def on_stitch_clicked(self, row, col):
        """Handle stitch click event"""
        # Get the current stitch type and color
        current_stitch_type, current_color_rgb = self.chart.get_stitch(
            row, col)
        current_color = QColor(*current_color_rgb)

        # Create and show the dialog
        dialog = StitchDialog(
            self.view,
            self.chart,
            row,
            col
        )

        if dialog.exec_():
            # Get the selected stitch type and color
            stitch_idx, color = dialog.get_selection()

            # Convert stitch index to name
            stitch_type = self.chart.STITCH_ORDER[stitch_idx]

            # Convert QColor to RGB tuple
            if color and color.isValid():
                color_rgb = (color.red(), color.green(), color.blue())

                # Use set_stitch to update both stitch type and color
                self.chart.set_stitch(
                    row, col, stitch_type=stitch_type, color_rgb=color_rgb)
            else:
                # Update only the stitch type
                self.chart.set_stitch(row, col, stitch_type=stitch_type)

            # Update the view
            self.update_chart()
