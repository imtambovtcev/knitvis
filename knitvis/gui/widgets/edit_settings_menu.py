from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QCheckBox, QLabel, QSlider, QPushButton,
                             QGroupBox, QFormLayout, QSpinBox, QComboBox,
                             QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal


class EditSettingsMenu(QDialog):
    """Settings dialog for chart views with general and view-specific options"""

    # Signal emitted when settings change
    settingsChanged = pyqtSignal(dict)

    def __init__(self, parent=None, view_type=None, current_settings=None):
        super().__init__(parent)
        self.view_type = view_type  # 'chart' or 'fabric'
        self.current_settings = current_settings or {}
        self.setWindowTitle("Edit Chart Settings")
        self.setMinimumWidth(350)
        self.init_ui()

    def init_ui(self):
        """Initialize the settings dialog UI"""
        layout = QVBoxLayout(self)

        # Create tabs for different settings categories
        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.view_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.view_tab, "View Settings")

        # Set up the general settings tab
        self.setup_general_tab()

        # Set up the view-specific settings tab
        if self.view_type == 'fabric':
            self.setup_fabric_view_tab()
        else:
            self.setup_chart_view_tab()

        layout.addWidget(self.tabs)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")

        self.ok_button.clicked.connect(self.accept_settings)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_settings)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

    def setup_general_tab(self):
        """Set up the general settings tab with options common to all views"""
        layout = QVBoxLayout(self.general_tab)

        # Display options
        display_group = QGroupBox("Display Options")
        display_layout = QFormLayout()

        self.show_row_numbers = QCheckBox()
        self.show_row_numbers.setChecked(
            self.current_settings.get('show_row_numbers', True))
        display_layout.addRow("Show Row Numbers:", self.show_row_numbers)

        self.show_col_numbers = QCheckBox()
        self.show_col_numbers.setChecked(
            self.current_settings.get('show_col_numbers', True))
        display_layout.addRow("Show Column Numbers:", self.show_col_numbers)

        # Add tick frequency controls
        self.x_axis_ticks_every_n = QSpinBox()
        self.x_axis_ticks_every_n.setRange(1, 10)
        self.x_axis_ticks_every_n.setValue(
            self.current_settings.get('x_axis_ticks_every_n', 1))
        display_layout.addRow("Column Tick Every:", self.x_axis_ticks_every_n)

        self.y_axis_ticks_every_n = QSpinBox()
        self.y_axis_ticks_every_n.setRange(1, 10)
        self.y_axis_ticks_every_n.setValue(
            self.current_settings.get('y_axis_ticks_every_n', 1))
        display_layout.addRow("Row Tick Every:", self.y_axis_ticks_every_n)

        self.x_axis_ticks_numbers_every_n_tics = QSpinBox()
        self.x_axis_ticks_numbers_every_n_tics.setRange(1, 10)
        self.x_axis_ticks_numbers_every_n_tics.setValue(
            self.current_settings.get('x_axis_ticks_numbers_every_n_tics', 1))
        display_layout.addRow("Column Number Every:",
                              self.x_axis_ticks_numbers_every_n_tics)

        self.y_axis_ticks_numbers_every_n_ticks = QSpinBox()
        self.y_axis_ticks_numbers_every_n_ticks.setRange(1, 10)
        self.y_axis_ticks_numbers_every_n_ticks.setValue(
            self.current_settings.get('y_axis_ticks_numbers_every_n_ticks', 1))
        display_layout.addRow("Row Number Every:",
                              self.y_axis_ticks_numbers_every_n_ticks)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Navigation options
        nav_group = QGroupBox("Navigation")
        nav_layout = QFormLayout()

        self.default_row_zoom = QSpinBox()
        self.default_row_zoom.setRange(5, 100)
        self.default_row_zoom.setValue(
            self.current_settings.get('default_row_zoom', 20))
        nav_layout.addRow("Default Row Zoom:", self.default_row_zoom)

        self.default_col_zoom = QSpinBox()
        self.default_col_zoom.setRange(5, 100)
        self.default_col_zoom.setValue(
            self.current_settings.get('default_col_zoom', 20))
        nav_layout.addRow("Default Column Zoom:", self.default_col_zoom)

        nav_group.setLayout(nav_layout)
        layout.addWidget(nav_group)

        layout.addStretch(1)

    def setup_chart_view_tab(self):
        """Set up chart view specific settings"""
        layout = QVBoxLayout(self.view_tab)

        # Appearance options
        appearance_group = QGroupBox("Chart Appearance")
        appearance_layout = QFormLayout()

        self.cell_border = QCheckBox()
        self.cell_border.setChecked(
            self.current_settings.get('cell_border', True))
        appearance_layout.addRow("Show Cell Borders:", self.cell_border)

        self.symbol_size = QSpinBox()
        self.symbol_size.setRange(8, 24)
        self.symbol_size.setValue(self.current_settings.get('symbol_size', 12))
        appearance_layout.addRow("Symbol Size:", self.symbol_size)

        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        layout.addStretch(1)

    def setup_fabric_view_tab(self):
        """Set up fabric view specific settings"""
        layout = QVBoxLayout(self.view_tab)

        # Stitch options
        stitch_group = QGroupBox("Stitch Appearance")
        stitch_layout = QFormLayout()

        self.show_outlines = QCheckBox()
        self.show_outlines.setChecked(
            self.current_settings.get('show_outlines', False))
        stitch_layout.addRow("Show Stitch Outlines:", self.show_outlines)

        # Use a double spin box for row spacing (direct value)
        self.row_spacing = QDoubleSpinBox()
        self.row_spacing.setRange(0.1, 1.0)
        self.row_spacing.setSingleStep(0.05)
        self.row_spacing.setDecimals(2)
        # Get direct value (now stored as a floating point value)
        self.row_spacing.setValue(
            self.current_settings.get('row_spacing', 0.7))
        stitch_layout.addRow("Row Spacing:", self.row_spacing)

        # Add padding control
        self.padding = QDoubleSpinBox()
        self.padding.setRange(0.001, 0.1)
        self.padding.setSingleStep(0.005)
        self.padding.setDecimals(3)
        self.padding.setValue(self.current_settings.get('padding', 0.01))
        stitch_layout.addRow("Stitch Padding:", self.padding)

        stitch_group.setLayout(stitch_layout)
        layout.addWidget(stitch_group)

        layout.addStretch(1)

    def get_settings(self):
        """Collect all settings into a dictionary"""
        settings = {
            'show_row_numbers': self.show_row_numbers.isChecked(),
            'show_col_numbers': self.show_col_numbers.isChecked(),
            'default_row_zoom': self.default_row_zoom.value(),
            'default_col_zoom': self.default_col_zoom.value(),
            'x_axis_ticks_every_n': self.x_axis_ticks_every_n.value(),
            'y_axis_ticks_every_n': self.y_axis_ticks_every_n.value(),
            'x_axis_ticks_numbers_every_n_tics': self.x_axis_ticks_numbers_every_n_tics.value(),
            'y_axis_ticks_numbers_every_n_ticks': self.y_axis_ticks_numbers_every_n_ticks.value(),
        }

        # Add view specific settings
        if self.view_type == 'fabric':
            settings.update({
                'show_outlines': self.show_outlines.isChecked(),
                # Store as direct value
                'row_spacing': self.row_spacing.value(),
                'padding': self.padding.value(),
            })
        else:
            settings.update({
                'cell_border': self.cell_border.isChecked(),
                'symbol_size': self.symbol_size.value(),
            })

        return settings

    def accept_settings(self):
        """Apply settings and close dialog"""
        self.apply_settings()
        self.accept()

    def apply_settings(self):
        """Apply the current settings without closing the dialog"""
        settings = self.get_settings()
        self.settingsChanged.emit(settings)
