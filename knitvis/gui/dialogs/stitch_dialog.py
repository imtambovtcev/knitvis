from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QPushButton, QLabel, QFormLayout, QDialogButtonBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from knitvis.gui.widgets.color_button import ColorButton


class StitchDialog(QDialog):
    """Dialog for editing stitch type and color"""

    def __init__(self, parent, chart, row, col):
        super().__init__(parent)
        self.chart = chart
        self.row = row
        self.col = col

        # Get current stitch info
        self.stitch_type, self.color_rgb = chart.get_stitch(row, col)

        self.setWindowTitle(f"Edit Stitch at Row {row+1}, Column {col+1}")
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Form layout for controls
        form = QFormLayout()

        # Stitch type selector
        self.stitch_combo = QComboBox()
        for stitch in self.chart.STITCH_ORDER:
            symbol = self.chart.STITCH_SYMBOLS.get(stitch, '?')
            self.stitch_combo.addItem(f"{stitch} ({symbol})", stitch)

        # Set the current stitch
        stitch_idx = self.chart.STITCH_ORDER.index(self.stitch_type)
        self.stitch_combo.setCurrentIndex(stitch_idx)

        form.addRow("Stitch Type:", self.stitch_combo)

        # Color selector
        self.color_button = ColorButton(initial_color=QColor(*self.color_rgb))
        form.addRow("Color:", self.color_button)

        layout.addLayout(form)

        # Preview
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Preview:")
        preview_layout.addWidget(preview_label)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(50, 50)
        self.preview_label.setStyleSheet("border: 1px solid black;")
        preview_layout.addWidget(self.preview_label)

        layout.addLayout(preview_layout)
        self.update_preview()

        # Connect signals
        self.stitch_combo.currentIndexChanged.connect(self.update_preview)
        self.color_button.colorChanged.connect(self.update_preview)

        # Standard buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setMinimumWidth(250)

    def update_preview(self):
        """Update the stitch preview"""
        # Get current selections
        stitch_idx = self.stitch_combo.currentIndex()
        stitch_type = self.chart.STITCH_ORDER[stitch_idx]
        symbol = self.chart.STITCH_SYMBOLS.get(stitch_type, '?')

        color = self.color_button.color

        # Create a stylesheet for the preview label
        bg_color = f"rgb({color.red()}, {color.green()}, {color.blue()})"

        # Calculate luminance to determine text color
        luminance = 0.2126 * color.red() + 0.7152 * color.green() + 0.0722 * color.blue()
        text_color = "black" if luminance > 128 else "white"

        self.preview_label.setStyleSheet(
            f"background-color: {bg_color}; "
            f"color: {text_color}; "
            f"font-size: 24px; "
            f"font-weight: bold; "
            f"border: 1px solid black;"
        )
        self.preview_label.setText(symbol)

    def get_selection(self):
        """Return the selected stitch type and color"""
        stitch_idx = self.stitch_combo.currentIndex()
        color = self.color_button.color

        return stitch_idx, color
