from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QPushButton)


class NewChartDialog(QDialog):
    """Dialog for creating a new chart with specified dimensions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("New Knitting Chart")
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        # Rows input
        rows_layout = QHBoxLayout()
        rows_layout.addWidget(QLabel("Rows:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(1, 1000)
        self.rows_spinbox.setValue(20)
        rows_layout.addWidget(self.rows_spinbox)
        layout.addLayout(rows_layout)

        # Columns input
        cols_layout = QHBoxLayout()
        cols_layout.addWidget(QLabel("Columns:"))
        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setRange(1, 1000)
        self.cols_spinbox.setValue(20)
        cols_layout.addWidget(self.cols_spinbox)
        layout.addLayout(cols_layout)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        ok_button = QPushButton("Create")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_dimensions(self):
        """Return the selected dimensions"""
        return self.rows_spinbox.value(), self.cols_spinbox.value()
