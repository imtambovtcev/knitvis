import pytest
import os
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication, QWidget

from knitvis.gui.settings_manager import SettingsManager
from knitvis.gui.dialogs.settings_dialog import SettingsDialog
from knitvis.gui.views import ChartView, FabricView
from knitvis import KnittingChart
import numpy as np


@pytest.fixture
def settings_manager():
    """Create a SettingsManager for testing."""
    # Use a different organization/app name for testing
    QSettings.setPath(QSettings.NativeFormat,
                      QSettings.UserScope, os.path.dirname(__file__))
    test_manager = SettingsManager()
    test_manager.settings = QSettings("KnitVisTest", "KnitVisTest")
    test_manager.settings.clear()
    return test_manager


@pytest.fixture
def sample_chart():
    """Create a sample chart for testing"""
    # Create a small test pattern
    pattern = np.zeros((5, 5), dtype=int)
    colors = np.full((5, 5, 3), [200, 200, 200], dtype=int)
    return KnittingChart(pattern, colors)


@pytest.fixture
def mock_parent():
    """Create a mock parent widget for the dialog."""
    return QWidget()


@pytest.fixture
def settings_dialog(qtbot, mock_parent, settings_manager):
    """Create a SettingsDialog for testing."""
    dialog = SettingsDialog(mock_parent, settings_manager)
    qtbot.addWidget(dialog)
    return dialog


def test_settings_default_values(settings_manager):
    """Test that default settings are returned when no values are set."""
    # Check defaults
    assert settings_manager.get('show_row_numbers') is True
    assert settings_manager.get('show_col_numbers') is True
    assert settings_manager.get('default_row_zoom') == 20
    assert settings_manager.get('chart_cell_border') is True
    assert settings_manager.get('fabric_row_spacing') == 0.7


def test_settings_set_get(settings_manager):
    """Test setting and getting values."""
    # Set some values
    settings_manager.set('show_row_numbers', False)
    settings_manager.set('default_row_zoom', 30)
    settings_manager.set('fabric_row_spacing', 0.5)

    # Check values are retrieved correctly
    assert settings_manager.get('show_row_numbers') is False
    assert settings_manager.get('default_row_zoom') == 30
    assert settings_manager.get('fabric_row_spacing') == 0.5


def test_settings_update(settings_manager):
    """Test updating multiple settings at once."""
    # Update multiple settings
    settings_manager.update({
        'show_row_numbers': False,
        'show_col_numbers': False,
        'chart_cell_border': False
    })

    # Check values are all updated
    assert settings_manager.get('show_row_numbers') is False
    assert settings_manager.get('show_col_numbers') is False
    assert settings_manager.get('chart_cell_border') is False


def test_settings_reset(settings_manager):
    """Test resetting settings to defaults."""
    # Change some settings
    settings_manager.set('show_row_numbers', False)
    settings_manager.set('chart_cell_border', False)
    settings_manager.set('fabric_row_spacing', 0.4)

    # Reset
    settings_manager.reset()

    # Check that values are back to defaults
    assert settings_manager.get('show_row_numbers') is True
    assert settings_manager.get('chart_cell_border') is True
    assert settings_manager.get('fabric_row_spacing') == 0.7


def test_settings_dialog_initialization(settings_dialog):
    """Test that the dialog initializes with correct settings."""
    # Check some key controls have default values
    assert settings_dialog.show_row_numbers.isChecked() is True
    assert settings_dialog.show_col_numbers.isChecked() is True
    assert settings_dialog.default_row_zoom.value() == 20
    assert settings_dialog.fabric_row_spacing.value() == 0.7


def test_settings_dialog_apply(qtbot, settings_dialog, settings_manager):
    """Test that applying settings from dialog updates the settings."""
    # Change some settings in dialog
    settings_dialog.show_row_numbers.setChecked(False)
    settings_dialog.fabric_row_spacing.setValue(0.6)

    # Check signal emission on apply
    with qtbot.waitSignal(settings_dialog.settingsApplied):
        settings_dialog.apply_settings()

    # Check settings manager values are updated
    assert settings_manager.get('show_row_numbers') is False
    assert settings_manager.get('fabric_row_spacing') == 0.6


def test_settings_dialog_reset(qtbot, settings_dialog, settings_manager):
    """Test that reset button resets settings to defaults."""
    # First change some settings
    settings_manager.set('show_row_numbers', False)
    settings_manager.set('chart_cell_border', False)
    settings_dialog.show_row_numbers.setChecked(False)
    settings_dialog.chart_cell_border.setChecked(False)

    # Reset
    with qtbot.waitSignal(settings_dialog.settingsApplied):
        settings_dialog.reset_settings()

    # Check controls are updated
    assert settings_dialog.show_row_numbers.isChecked() is True
    assert settings_dialog.chart_cell_border.isChecked() is True


def test_view_settings_application(settings_manager, sample_chart):
    """Test that view-specific settings are correctly applied to views."""
    # Set some specific view settings
    settings_manager.set('show_row_numbers', False)
    settings_manager.set('chart_symbol_size', 16)
    settings_manager.set('fabric_row_spacing', 0.5)

    # Get view settings
    chart_settings = settings_manager.get_view_settings('chart')
    fabric_settings = settings_manager.get_view_settings('fabric')

    # Create views with these settings
    chart_view = ChartView(sample_chart)
    chart_view.settings.update(chart_settings)

    fabric_view = FabricView(sample_chart)
    fabric_view.settings.update(fabric_settings)

    # Check settings are applied correctly
    assert chart_view.settings['show_row_numbers'] is False
    assert chart_view.settings['symbol_size'] == 16
    assert fabric_view.settings['show_row_numbers'] is False
    assert fabric_view.settings['row_spacing'] == 0.5
