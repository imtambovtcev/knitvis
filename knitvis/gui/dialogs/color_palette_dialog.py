from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QColorDialog,
                             QListWidgetItem, QFrame, QSplitter, QWidget)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import numpy as np


class ColorItemWidget(QWidget):
    """Custom widget for displaying a color in the list"""

    def __init__(self, color_tuple, color_name, color_tag, parent=None):
        super().__init__(parent)
        self.color_rgb = color_tuple
        self.color_name = color_name
        self.color_tag = color_tag
        self.color = QColor(*color_tuple)

        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        # Color swatch
        self.swatch = QFrame()
        self.swatch.setFixedSize(30, 30)
        self.swatch.setFrameShape(QFrame.Box)
        self.swatch.setAutoFillBackground(True)

        # Use a completely new palette
        palette = QPalette()
        palette.setColor(QPalette.Window, self.color)
        self.swatch.setPalette(palette)

        layout.addWidget(self.swatch)

        # Color info
        info_layout = QVBoxLayout()
        self.name_label = QLabel(f"{color_name} ({color_tag})")
        self.rgb_label = QLabel(
            f"RGB: {color_tuple[0]}, {color_tuple[1]}, {color_tuple[2]}")
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.rgb_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        self.setLayout(layout)

    def update_color(self, new_color_tuple):
        """Update the displayed color"""
        self.color_rgb = new_color_tuple
        self.color = QColor(*new_color_tuple)

        # Use a completely new palette to ensure color is set correctly
        palette = QPalette()
        palette.setColor(QPalette.Window, self.color)
        self.swatch.setPalette(palette)

        # Update RGB label
        self.rgb_label.setText(
            f"RGB: {new_color_tuple[0]}, {new_color_tuple[1]}, {new_color_tuple[2]}")


class ColorPaletteDialog(QDialog):
    """Dialog for managing the color palette"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.chart = parent.chart if hasattr(parent, 'chart') else None
        self.modified_colors = {}

        self.init_ui()
        self.load_color_palette()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Color Palette")
        self.resize(700, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left side - color list
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        left_layout.addWidget(QLabel("Available Colors:"))

        self.color_list = QListWidget()
        self.color_list.setMinimumWidth(300)
        self.color_list.currentRowChanged.connect(self.on_color_selected)
        left_layout.addWidget(self.color_list)

        # Color modification buttons
        button_layout = QHBoxLayout()
        self.edit_color_button = QPushButton("Edit Color")
        self.edit_color_button.clicked.connect(self.edit_selected_color)
        self.edit_color_button.setEnabled(False)

        button_layout.addWidget(self.edit_color_button)
        button_layout.addStretch()
        left_layout.addLayout(button_layout)

        # Right side - palette visualization
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        right_layout.addWidget(QLabel("Palette Preview:"))

        self.figure, self.ax = plt.subplots(figsize=(5, 2))
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_settings)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def load_color_palette(self):
        """Load the current color palette from the chart"""
        if not self.chart:
            return

        # Clear existing items
        self.color_list.clear()

        # Add colors from chart's palette
        palette = self.chart.color_palette

        for i in range(palette.num_colors):
            color_rgb = palette.get_color_rgb_by_index(i)
            color_name = palette.full_names[i]
            color_tag = palette.short_tags[i]

            # Create item and widget
            item = QListWidgetItem()
            item_widget = ColorItemWidget(color_rgb, color_name, color_tag)

            # Set size and add to list
            item.setSizeHint(item_widget.sizeHint())
            self.color_list.addItem(item)
            self.color_list.setItemWidget(item, item_widget)

        # Update the palette visualization
        self.update_palette_preview()

    def update_palette_preview(self):
        """Update the palette visualization figure"""
        if not self.chart:
            return

        palette = self.chart.color_palette

        # Clear the figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # No colors to display
        if palette.num_colors == 0:
            ax.text(0.5, 0.5, "No colors in palette", ha='center', va='center')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return

        # Draw color swatches
        for i in range(palette.num_colors):
            color = palette.get_color_rgb_by_index(i)
            normalized_rgb = [c / 255 for c in color]
            ax.add_patch(plt.Rectangle(
                (i, 0), 1, 1, color=normalized_rgb, edgecolor='black'))

            # Add tag label
            ax.text(i + 0.5, -0.2, f"{palette.short_tags[i]}",
                    ha='center', va='center', fontsize=9)

        # Set figure limits and appearance
        ax.set_xlim(0, palette.num_colors)
        ax.set_ylim(-0.5, 1.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        self.figure.tight_layout()
        self.canvas.draw()

    def on_color_selected(self, row):
        """Handle color selection in the list"""
        # Enable/disable buttons based on selection
        has_selection = row >= 0
        self.edit_color_button.setEnabled(has_selection)

    def edit_selected_color(self):
        """Edit the currently selected color"""
        current_row = self.color_list.currentRow()
        if current_row < 0:
            return

        # Get the current color widget
        item = self.color_list.item(current_row)
        item_widget = self.color_list.itemWidget(item)

        # Open color dialog with current color
        current_color = QColor(*item_widget.color_rgb)
        color = QColorDialog.getColor(current_color, self, "Select Color")

        if color.isValid():
            # Update color in the list widget
            new_color_tuple = (color.red(), color.green(), color.blue())
            item_widget.update_color(new_color_tuple)

            # Update color in the chart palette (but don't apply until Apply/OK)
            self.modified_colors[current_row] = new_color_tuple

            # Preview the change
            self.preview_color_changes()

    def preview_color_changes(self):
        """Preview color changes without applying them permanently"""
        if not self.modified_colors or not self.chart:
            return

        # Create a temporary copy of the palette for preview
        palette = self.chart.color_palette
        preview_colors = [palette.get_color_by_index(
            i) for i in range(palette.num_colors)]

        # Apply modifications to the preview
        for idx, color in self.modified_colors.items():
            preview_colors[idx] = color

        # Update the preview with modified colors
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        for i, color in enumerate(preview_colors):
            normalized_rgb = [c / 255 for c in color]
            ax.add_patch(plt.Rectangle(
                (i, 0), 1, 1, color=normalized_rgb, edgecolor='black'))
            ax.text(i + 0.5, -0.2, f"{palette.short_tags[i]}",
                    ha='center', va='center', fontsize=9)

        ax.set_xlim(0, len(preview_colors))
        ax.set_ylim(-0.5, 1.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)

        self.figure.tight_layout()
        self.canvas.draw()

    def apply_settings(self):
        """Apply changes to the chart"""
        if not self.chart:
            return

        # Apply color modifications
        for idx, new_color in self.modified_colors.items():
            # Find all stitches using this color
            color_indices = (self.chart.color_indices == idx)
            rows, cols = np.where(color_indices)

            # Update each stitch with the new color
            for r, c in zip(rows, cols):
                self.chart.set_stitch(r, c, color_rgb=new_color)

        # Clear the modifications after applying
        self.modified_colors = {}

        # Update the views if needed
        if hasattr(self.parent, 'controllers'):
            for controller in self.parent.controllers:
                controller.update_chart()

        # Refresh our own display
        self.load_color_palette()

    def accept(self):
        """Apply settings and close dialog"""
        self.apply_settings()
        super().accept()
