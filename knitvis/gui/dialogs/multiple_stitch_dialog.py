from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QPushButton, QLabel, QFormLayout, QDialogButtonBox,
                             QCheckBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from knitvis.gui.widgets.color_button import ColorButton


class MultipleStitchDialog(QDialog):
    """Dialog for editing multiple stitches at once"""

    def __init__(self, parent, chart, selected_stitches):
        super().__init__(parent)
        self.chart = chart
        self.selected_stitches = selected_stitches

        self.setWindowTitle(f"Edit {len(selected_stitches)} Stitches")
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Form layout for controls
        form = QFormLayout()

        # Stitch type selector with "Keep existing" option
        self.stitch_enabled = QCheckBox("Change stitch type")
        self.stitch_enabled.setChecked(False)
        form.addRow("", self.stitch_enabled)

        self.stitch_combo = QComboBox()
        for stitch in self.chart.STITCH_ORDER:
            symbol = self.chart.STITCH_SYMBOLS.get(stitch, '?')
            self.stitch_combo.addItem(f"{stitch} ({symbol})", stitch)
        self.stitch_combo.setEnabled(False)
        form.addRow("New Stitch Type:", self.stitch_combo)

        # Connect checkbox to enable/disable stitch combo
        self.stitch_enabled.toggled.connect(self.stitch_combo.setEnabled)

        # Color selector with "Keep existing" option
        self.color_enabled = QCheckBox("Change color")
        self.color_enabled.setChecked(False)
        form.addRow("", self.color_enabled)

        # Default to medium gray color
        self.color_button = ColorButton(initial_color=QColor(128, 128, 128))
        self.color_button.setEnabled(False)
        form.addRow("New Color:", self.color_button)

        # Connect checkbox to enable/disable color button
        self.color_enabled.toggled.connect(self.color_button.setEnabled)

        layout.addLayout(form)

        # Standard buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Add a summary label
        self.summary_label = QLabel(
            f"{len(self.selected_stitches)} stitches selected")
        self.summary_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.summary_label)

        self.setMinimumWidth(300)

    def get_selection(self):
        """Return the selected stitch type and color, or None if not changing"""
        stitch_idx = None
        if self.stitch_enabled.isChecked():
            stitch_idx = self.stitch_combo.currentIndex()

        color = None
        if self.color_enabled.isChecked():
            color = self.color_button.color

        return stitch_idx, color
