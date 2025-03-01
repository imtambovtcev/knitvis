from PyQt5.QtWidgets import QPushButton, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal


class ColorButton(QPushButton):
    """Button that opens a color picker dialog when clicked"""

    # Signal emitted when color changes
    colorChanged = pyqtSignal(QColor)

    def __init__(self, initial_color=None, parent=None):
        super().__init__(parent)
        self.color = initial_color or QColor(128, 128, 128)
        self.setFixedSize(30, 30)
        self.update_button()
        self.clicked.connect(self.choose_color)

    def update_button(self):
        """Update button appearance to reflect current color"""
        self.setStyleSheet(
            f"background-color: rgb({self.color.red()}, {self.color.green()}, {self.color.blue()}); "
            f"border: 1px solid black;"
        )

    def choose_color(self):
        """Open color picker and update color"""
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.set_color(color)

    def set_color(self, color):
        """Set button color and emit signal"""
        if color != self.color:
            self.color = color
            self.update_button()
            self.colorChanged.emit(color)
