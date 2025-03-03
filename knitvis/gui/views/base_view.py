from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMenu, QAction
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor

from knitvis.chart import KnittingChart
from knitvis.gui.widgets.chart_navigation import ChartNavigationWidget
from knitvis.gui.views.chart_debug import debug_print, check_renderer_ready


class BaseChartView(QWidget):
    """Base class for all chart visualization views"""

    # Signals for interaction
    stitch_clicked = pyqtSignal(int, int)  # Row, column
    multiple_stitches_selected = pyqtSignal(list)  # List of (row, col) tuples

    def __init__(self, chart=None):
        super().__init__()
        self.chart = chart

        # Initialize caching for better performance
        self._cache = {}
        self._background = None

        # Initialize selection tracking
        self.selected_stitches = []  # List of (row, col) tuples
        self.selection_active = False  # True when shift is pressed
        self.selection_rect = None  # For drawing selection rectangle
        self.selection_markers = []  # For drawing selection markers
        self.selecting = False  # True during selection rectangle drag

        # Use grid layout instead of vertical layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Initialize default settings BEFORE calling init_ui
        self.settings = {
            'show_row_numbers': True,
            'show_col_numbers': True,
            'default_row_zoom': 20,
            'default_col_zoom': 20
        }

        # Create navigation widget which will contain the chart view
        self.navigation = ChartNavigationWidget()
        self.navigation.viewportChanged.connect(self.on_viewport_changed)

        # The navigation widget is now the main container
        self.layout.addWidget(self.navigation, 0, 0)

        # Initialize the UI (specific to each view)
        self.init_ui()

        if chart:
            self.update_view()

    def init_ui(self):
        """Initialize the UI components - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement init_ui")

    def update_view(self):
        """Update the view with current chart data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement update_view")

    def draw_selection_markers(self):
        """Draw markers for selected stitches - to be implemented by subclasses"""
        raise NotImplementedError(
            "Subclasses must implement draw_selection_markers")

    def clear_selection(self):
        """Clear all selected stitches"""
        if self.selected_stitches:
            self.selected_stitches = []
            self.clear_selection_markers()  # Just clear markers, don't redraw

    def add_to_selection(self, row, col):
        """Add a stitch to the current selection if not already selected"""
        if (row, col) not in self.selected_stitches:
            self.selected_stitches.append((row, col))
            self.update_selection_markers()  # Update markers only

    def set_selection(self, row, col):
        """Set selection to a single stitch (clear any previous selection)"""
        self.selected_stitches = [(row, col)]
        self.update_selection_markers()  # Update markers only

    def toggle_selection(self, row, col):
        """Toggle selection for a stitch"""
        if (row, col) in self.selected_stitches:
            self.selected_stitches.remove((row, col))
        else:
            self.selected_stitches.append((row, col))
        self.update_selection_markers()  # Update markers only

    def update_selection_markers(self):
        """Update the selection markers without redrawing the entire view"""
        self.clear_selection_markers()  # Remove existing markers
        self.draw_selection_markers()   # Draw new markers

    def clear_selection_markers(self):
        """Clear only the selection markers without affecting the main view"""
        # Remove any existing markers
        for marker in self.selection_markers:
            try:
                marker.remove()
            except:
                # Handle any errors during removal
                pass
        self.selection_markers = []

        # Redraw the canvas to remove the markers
        if hasattr(self, 'canvas'):
            self.canvas.draw()

    def show_context_menu(self, event, chart_row, chart_col):
        """Show context menu for stitches"""
        menu = QMenu(self)

        # Create basic menu actions
        if len(self.selected_stitches) <= 1:
            # Single stitch selection actions
            title_action = QAction(
                f"Stitch at Row {chart_row+1}, Column {chart_col+1}", self)
            title_action.setEnabled(False)
            menu.addAction(title_action)
            menu.addSeparator()

            edit_action = QAction("Edit Stitch...", self)
            edit_action.triggered.connect(
                lambda: self.stitch_clicked.emit(chart_row, chart_col))
            menu.addAction(edit_action)
        else:
            # Multiple stitch selection actions
            title_action = QAction(
                f"{len(self.selected_stitches)} Stitches Selected", self)
            title_action.setEnabled(False)
            menu.addAction(title_action)
            menu.addSeparator()

            edit_action = QAction("Edit Selected Stitches...", self)
            edit_action.triggered.connect(
                lambda: self.multiple_stitches_selected.emit(self.selected_stitches))
            menu.addAction(edit_action)

        # Add selection actions
        menu.addSeparator()
        clear_action = QAction("Clear Selection", self)
        clear_action.triggered.connect(self.clear_selection)
        menu.addAction(clear_action)

        menu.exec_(self.canvas.mapToGlobal(event.pos()))

    def handle_click(self, event, chart_row, chart_col):
        """Handle mouse click on chart coordinates"""
        # Fix: event.button is a property, not a method
        if event.button == 1:  # Left button (1 in matplotlib)
            # Matplotlib events use 'shift' in the modifiers frozenset, not Qt modifiers
            if 'shift' in event.modifiers:
                # Add to selection with shift key
                self.toggle_selection(chart_row, chart_col)
            else:
                # Regular click - select single stitch
                self.set_selection(chart_row, chart_col)
                # Also emit the stitch clicked signal for single clicks
                self.stitch_clicked.emit(chart_row, chart_col)
        elif event.button == 3:  # Right button (3 in matplotlib)
            # Right click - show context menu
            # If clicking on unselected stitch, select it first
            if (chart_row, chart_col) not in self.selected_stitches:
                self.set_selection(chart_row, chart_col)
            self.show_context_menu(event, chart_row, chart_col)

    def set_chart(self, chart):
        """Set a new chart and update the view"""
        self.chart = chart
        self.selected_stitches = []  # Clear selection when setting new chart
        self.update_navigation_limits()
        self.update_view()

    def update_navigation_limits(self):
        """Update navigation limits based on chart dimensions"""
        if self.chart:
            self.navigation.update_navigation_limits(
                self.chart.rows, self.chart.cols)

    def on_viewport_changed(self, row, col, row_zoom, col_zoom):
        """Handle viewport parameter changes from navigation widget"""
        # Force a complete redraw when the viewport changes
        # This ensures all traces from previous views are cleared
        if hasattr(self, 'figure'):
            self.figure.clear()

        # Reset all caches and tracking
        self.clear_cache()
        self.clear_selection_markers()

        # Now call the view update
        self.update_view()

    def get_viewport_parameters(self):
        """Get the current viewport parameters (row, col, row_zoom, col_zoom)"""
        return (
            self.navigation.row_pos.value(),
            self.navigation.col_pos.value(),
            self.navigation.row_zoom_slider.value(),
            self.navigation.col_zoom_slider.value()
        )

    def get_view_type(self):
        """Return the view type for settings (implemented by subclasses)"""
        return 'base'

    def apply_settings(self, settings):
        """Apply new settings to the view"""
        self.settings.update(settings)
        self.update_view()

    def clear_cache(self):
        """Clear the cached objects"""
        self._cache.clear()
        self._background = None

    def cache_background(self):
        """Cache the static background for blitting"""
        if hasattr(self, 'canvas') and hasattr(self, 'ax'):
            try:
                # Make sure we have a renderer
                if hasattr(self.canvas, 'renderer') and self.canvas.renderer is not None:
                    # Copy the renderer state to a background buffer
                    self._background = self.canvas.copy_from_bbox(self.ax.bbox)
                    debug_print("Background cached successfully")
                    return True
                else:
                    # We don't have a renderer yet, probably first draw
                    debug_print("Canvas renderer not ready yet")
                    self._background = None
            except Exception as e:
                debug_print(f"Error caching background: {e}")
                self._background = None
        return False

    def restore_background(self):
        """Restore the cached background for blitting"""
        if self._background is not None and hasattr(self, 'canvas'):
            try:
                self.canvas.restore_region(self._background)
                return True
            except Exception as e:
                debug_print(f"Error restoring background: {e}")
                self._background = None  # Clear invalid background
        return False

    def keyPressEvent(self, event):
        """Handle key press events for selection mode"""
        if event.key() == Qt.Key_Shift:
            self.selection_active = True
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Handle key release events for selection mode"""
        if event.key() == Qt.Key_Shift:
            self.selection_active = False
        super().keyReleaseEvent(event)

    def showEvent(self, event):
        """Handle show event by updating the view if needed"""
        super().showEvent(event)

        # Only update if we have a chart
        if self.chart:
            # Update the view when the widget becomes visible
            self.update_view()

            # Print debug info
            print(f"View {self.__class__.__name__} shown, updated view")
