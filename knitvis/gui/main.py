import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QAction,
                             QFileDialog, QMessageBox, QVBoxLayout, QWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings

from knitvis.chart import KnittingChart
from knitvis.gui.views import ChartView, FabricView
from knitvis.gui.controllers import ChartController, FabricController


class KnitVisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chart = None
        self.settings = QSettings("KnitVis", "KnitVis")
        self.controllers = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("KnitVis - Knitting Pattern Visualization")
        self.setGeometry(100, 100, 900, 700)

        # Create menu bar
        self.create_menu_bar()

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create a dummy chart to start with
        self.create_new_chart(rows=10, cols=10)

        self.show()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        new_action = QAction('&New Chart', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_chart)
        file_menu.addAction(new_action)

        open_action = QAction('&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_chart)
        file_menu.addAction(open_action)

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_chart)
        file_menu.addAction(save_action)

        save_as_action = QAction('Save &As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_chart_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu('&Edit')

        color_palette_action = QAction('&Color Palette', self)
        color_palette_action.triggered.connect(self.show_color_palette)
        edit_menu.addAction(color_palette_action)

    def create_new_chart(self, rows=10, cols=10):
        """Create a new chart with the specified dimensions"""
        import numpy as np

        # Create a blank chart with all knit stitches
        # All knit stitches (index 0)
        pattern = np.zeros((rows, cols), dtype=int)
        colors = np.full((rows, cols, 3), [
                         200, 200, 200], dtype=int)  # Light gray
        self.chart = KnittingChart(pattern, colors)

        # Clear existing tabs
        self.tab_widget.clear()
        self.controllers.clear()

        # Create tabs for different visualizations
        self.setup_tabs()

    def setup_tabs(self):
        """Set up the visualization tabs"""
        if not self.chart:
            return

        # Create Chart View Tab
        chart_view = ChartView(self.chart)
        chart_controller = ChartController(chart_view, self.chart)
        self.controllers.append(chart_controller)
        self.tab_widget.addTab(chart_view, "Chart View")

        # Create Fabric View Tab
        fabric_view = FabricView(self.chart)
        fabric_controller = FabricController(fabric_view, self.chart)
        self.controllers.append(fabric_controller)
        self.tab_widget.addTab(fabric_view, "Fabric View")

    def new_chart(self):
        """Create a new chart, prompting for dimensions"""
        from knitvis.gui.dialogs import NewChartDialog

        dialog = NewChartDialog(self)
        if dialog.exec_():
            rows, cols = dialog.get_dimensions()
            self.create_new_chart(rows, cols)

    def open_chart(self):
        """Open a chart from a file"""
        last_dir = self.settings.value("last_directory", "")

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Knitting Chart", last_dir,
            "Knitting Chart Files (*.json);;All Files (*)")

        if file_path:
            try:
                self.chart = KnittingChart.from_json(file_path)
                self.settings.setValue(
                    "last_directory", os.path.dirname(file_path))
                self.settings.setValue("last_file", file_path)
                self.setup_tabs()
            except Exception as e:
                QMessageBox.critical(self, "Error Opening File",
                                     f"Could not open the file: {str(e)}")

    def save_chart(self):
        """Save the chart to the current file or prompt for a new file"""
        last_file = self.settings.value("last_file", "")

        if last_file:
            self._save_to_file(last_file)
        else:
            self.save_chart_as()

    def save_chart_as(self):
        """Save the chart to a new file"""
        if not self.chart:
            return

        last_dir = self.settings.value("last_directory", "")

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Knitting Chart", last_dir,
            "Knitting Chart Files (*.json);;All Files (*)")

        if file_path:
            self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        """Save the chart to the specified file"""
        try:
            self.chart.save_to_json(file_path)
            self.settings.setValue(
                "last_directory", os.path.dirname(file_path))
            self.settings.setValue("last_file", file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving File",
                                 f"Could not save the file: {str(e)}")

    def show_color_palette(self):
        """Show the color palette dialog"""
        from knitvis.gui.dialogs import ColorPaletteDialog

        dialog = ColorPaletteDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("KnitVis")
    app.setOrganizationName("KnitVis")

    window = KnitVisApp()
    sys.exit(app.exec_())
