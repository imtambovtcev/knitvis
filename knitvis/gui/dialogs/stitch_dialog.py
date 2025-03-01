from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QColorDialog, QFrame)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt


class ColorButton(QPushButton):
    """Button that shows and allows selection of a color"""

    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.color = color or QColor(128, 128, 128)
        self.setFixedSize(50, 30)
        self.update_button_color()

    def update_button_color(self):
        """Update the button background to show the current color"""
        palette = self.palette()
        palette.setColor(QPalette.Button, self.color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_color(self, color):
        """Set a new color and update display"""
        self.color = color
        self.update_button_color()


class StitchDialog(QDialog):
    """Dialog for editing a stitch's type and color"""

    def __init__(self, parent, chart, row, col):
        super().__init__(parent)
        self.chart = chart
        self.row = row
        self.col = col

        # Get current stitch type and color using the new get_stitch method
        stitch_type, color_rgb = self.chart.get_stitch(row, col)
        self.stitch_index = self.chart.STITCH_ORDER.index(stitch_type)
        self.current_color = QColor(*color_rgb)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Edit Stitch")
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        # Stitch type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Stitch Type:"))
        self.stitch_combo = QComboBox()

        for stitch in self.chart.STITCH_ORDER:
            symbol = self.chart.STITCH_SYMBOLS[stitch]
            self.stitch_combo.addItem(f"{stitch} ({symbol})")

        self.stitch_combo.setCurrentIndex(self.stitch_index)
        type_layout.addWidget(self.stitch_combo)
        layout.addLayout(type_layout)

        # Color selection
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_button = ColorButton(self.current_color)
        self.color_button.clicked.connect(self.select_color)
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)

        # Preview
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.preview_frame = QFrame()
        self.preview_frame.setFixedSize(40, 40)
        self.preview_frame.setFrameShape(QFrame.Box)
        self.update_preview()
        preview_layout.addWidget(self.preview_frame)
        layout.addLayout(preview_layout)

        # Position info
        position_label = QLabel(
            f"Position: Row {self.row + 1}, Column {self.col + 1}")
        layout.addWidget(position_label)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals
        self.stitch_combo.currentIndexChanged.connect(self.update_preview)

    def select_color(self):
        """Open color dialog and update if a color is selected"""
        color = QColorDialog.getColor(self.color_button.color)
        if color.isValid():
            self.color_button.set_color(color)
            self.update_preview()

    def update_preview(self):
        """Update the preview of the stitch"""
        # Get selected stitch symbol
        stitch_idx = self.stitch_combo.currentIndex()
        stitch_key = self.chart.STITCH_ORDER[stitch_idx]
        symbol = self.chart.STITCH_SYMBOLS[stitch_key]

        # Set background color
        palette = self.preview_frame.palette()
        palette.setColor(QPalette.Window, self.color_button.color)
        self.preview_frame.setPalette(palette)
        self.preview_frame.setAutoFillBackground(True)

        # Check if we need to use white or black text based on background
        rgb = self.color_button.color.getRgb()[:3]
        luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        text_color = Qt.black if luminance > 128 else Qt.white

        # Clear any existing label and add a new one
        for child in self.preview_frame.children():
            if isinstance(child, QLabel):
                child.deleteLater()

        label = QLabel(symbol, self.preview_frame)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"color: {'black' if text_color == Qt.black else 'white'}; font-size: 18pt; font-weight: bold;")
        label.setGeometry(0, 0, 40, 40)

    def get_selection(self):
        """Return the selected stitch type and color"""
        return self.stitch_combo.currentIndex(), self.color_button.color
