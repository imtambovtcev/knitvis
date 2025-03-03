import json
import os
from pathlib import Path
from PyQt5.QtCore import QSettings


class SettingsManager:
    """Manages application settings with default values"""

    def __init__(self):
        self.settings = QSettings("KnitVis", "KnitVis")
        self.defaults = {
            # General settings
            'show_row_numbers': True,
            'show_col_numbers': True,
            'default_row_zoom': 20,
            'default_col_zoom': 20,
            'x_axis_ticks_every_n': 1,
            'y_axis_ticks_every_n': 1,
            'x_axis_ticks_numbers_every_n_tics': 1,
            'y_axis_ticks_numbers_every_n_ticks': 1,
            'opacity': 1.0,  # Default opacity - fully opaque

            # Chart view settings
            'chart_cell_border': True,
            'chart_symbol_size': 12,
            'chart_opacity': 1.0,  # Chart-specific opacity

            # Fabric view settings
            'fabric_show_outlines': False,
            'fabric_row_spacing': 0.7,  # Direct value (not percentage)
            'fabric_padding': 0.01,
            'fabric_opacity': 1.0,  # Fabric-specific opacity
        }

    def get(self, key, default=None):
        """Get a setting value with fallback to defaults"""
        if default is None and key in self.defaults:
            default = self.defaults[key]

        value = self.settings.value(key, default)

        # Ensure proper type conversion for booleans and numbers
        if isinstance(default, bool) and not isinstance(value, bool):
            # Handle QSettings' string representation of booleans
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 't', 'y')
            return bool(value)
        elif isinstance(default, int) and not isinstance(value, int):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif isinstance(default, float) and not isinstance(value, float):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        return value

    def set(self, key, value):
        """Set a setting value"""
        self.settings.setValue(key, value)

    def update(self, settings_dict):
        """Update multiple settings at once"""
        for key, value in settings_dict.items():
            self.set(key, value)

    def reset(self):
        """Reset settings to defaults"""
        self.settings.clear()
        self.update(self.defaults)

    def get_view_settings(self, view_type):
        """Get settings for a specific view type"""
        common_settings = {
            'show_row_numbers': self.get('show_row_numbers'),
            'show_col_numbers': self.get('show_col_numbers'),
            'default_row_zoom': self.get('default_row_zoom'),
            'default_col_zoom': self.get('default_col_zoom'),
            'x_axis_ticks_every_n': self.get('x_axis_ticks_every_n'),
            'y_axis_ticks_every_n': self.get('y_axis_ticks_every_n'),
            'x_axis_ticks_numbers_every_n_tics': self.get('x_axis_ticks_numbers_every_n_tics'),
            'y_axis_ticks_numbers_every_n_ticks': self.get('y_axis_ticks_numbers_every_n_ticks'),
            'opacity': self.get('opacity'),  # General opacity setting
        }

        if view_type == 'chart':
            return {
                **common_settings,
                'cell_border': self.get('chart_cell_border'),
                'symbol_size': self.get('chart_symbol_size'),
                # Override with chart-specific opacity
                'opacity': self.get('chart_opacity'),
            }
        elif view_type == 'fabric':
            return {
                **common_settings,
                'show_outlines': self.get('fabric_show_outlines'),
                'row_spacing': self.get('fabric_row_spacing'),  # Direct value
                'padding': self.get('fabric_padding'),
                # Override with fabric-specific opacity
                'opacity': self.get('fabric_opacity'),
            }
        else:
            return common_settings
