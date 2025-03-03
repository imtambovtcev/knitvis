from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QCheckBox,
                             QSlider, QGroupBox, QFormLayout, QDoubleSpinBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal
import os


class BackgroundImageDialog(QDialog):
    """Dialog for selecting and configuring background images for charts"""

    # Signal when settings are applied
    settingsApplied = pyqtSignal(dict)

    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.image_path = self.current_settings.get(
            'background_image_path', '')
        self.setWindowTitle("Background Image Settings")
        self.setMinimumWidth(450)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Image selection group
        image_group = QGroupBox("Background Image")
        image_layout = QVBoxLayout()

        # Enable background image checkbox
        self.enable_background = QCheckBox("Enable Background Image")
        self.enable_background.setChecked(
            self.current_settings.get('background_image_enabled', False))
        self.enable_background.toggled.connect(self.toggle_controls)
        image_layout.addWidget(self.enable_background)

        # File selection
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel(self.image_path or "No image selected")
        self.file_path_label.setWordWrap(True)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_image)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.browse_button)
        image_layout.addLayout(file_layout)

        # Preview (small thumbnail)
        self.image_preview = QLabel("Image Preview")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumHeight(150)
        self.image_preview.setStyleSheet("border: 1px solid gray")
        image_layout.addWidget(self.image_preview)

        # Update preview if image path exists
        if self.image_path and os.path.exists(self.image_path):
            self.update_preview()

        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        # Image display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()

        # Opacity control
        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.1, 1.0)
        self.opacity.setSingleStep(0.05)
        self.opacity.setDecimals(2)
        self.opacity.setValue(self.current_settings.get(
            'background_image_opacity', 0.3))
        display_layout.addRow("Opacity:", self.opacity)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")
        self.remove_button = QPushButton("Remove Image")

        self.ok_button.clicked.connect(self.accept_settings)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_settings)
        self.remove_button.clicked.connect(self.remove_image)

        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

        # Initialize control states
        self.toggle_controls(self.enable_background.isChecked())

    def toggle_controls(self, enabled):
        """Enable or disable controls based on checkbox state"""
        self.browse_button.setEnabled(enabled)
        self.opacity.setEnabled(enabled)
        self.remove_button.setEnabled(enabled and bool(self.image_path))

    def browse_image(self):
        """Open file dialog to select a background image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Image",
            os.path.dirname(self.image_path) if self.image_path else "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if file_path:
            self.image_path = file_path
            self.file_path_label.setText(file_path)
            self.remove_button.setEnabled(True)
            self.update_preview()

    def update_preview(self):
        """Update the image preview thumbnail"""
        if not self.image_path or not os.path.exists(self.image_path):
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            self.image_preview.setText("Failed to load image")
            return

        # Scale the pixmap to fit the preview area, maintaining aspect ratio
        preview_height = self.image_preview.height()
        preview_width = self.image_preview.width()
        pixmap = pixmap.scaled(preview_width, preview_height,
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_preview.setPixmap(pixmap)

    def remove_image(self):
        """Clear the selected background image"""
        self.image_path = ""
        self.file_path_label.setText("No image selected")
        self.image_preview.clear()
        self.image_preview.setText("Image Preview")
        self.remove_button.setEnabled(False)

    def get_settings(self):
        """Collect all settings into a dictionary"""
        return {
            'background_image_enabled': self.enable_background.isChecked(),
            'background_image_path': self.image_path,
            'background_image_opacity': self.opacity.value(),
        }

    def accept_settings(self):
        """Apply settings and close dialog"""
        self.apply_settings()
        self.accept()

    def apply_settings(self):
        """Apply the current settings without closing the dialog"""
        settings = self.get_settings()

        # Add debug logs
        print(f"Background image settings: {settings}")
        if settings['background_image_enabled']:
            print(
                f"Background image path exists: {os.path.exists(settings['background_image_path'])}")

        self.settingsApplied.emit(settings)

    def resizeEvent(self, event):
        """Handle resize events to update the image preview"""
        super().resizeEvent(event)
        if self.image_path and os.path.exists(self.image_path):
            self.update_preview()
