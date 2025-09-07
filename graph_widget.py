# graph_widget.py
"""
Custom graph widget with hover functionality for displaying ping data.
"""

import numpy as np
from datetime import timedelta
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton
import pyqtgraph as pg
from pyqtgraph import PlotWidget, TextItem
from constants import Colors


class ResetViewButton(QPushButton):
    """Small reset view button for the graph widget"""
    
    def __init__(self, parent=None):
        super().__init__("Reset View", parent)
        self.setMinimumHeight(32)
        self.setMaximumHeight(32)
        self.setMaximumWidth(110)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.setToolTip("Reset graph view to auto-range mode")
        self._setup_style()
        
    def _setup_style(self):
        """Setup button styling to match primary buttons"""
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {Colors.PRIMARY_BLUE}, stop: 1 {Colors.PRIMARY_BLUE_PRESSED});
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {Colors.PRIMARY_BLUE_HOVER}, stop: 1 {Colors.PRIMARY_BLUE});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {Colors.PRIMARY_BLUE_PRESSED}, stop: 1 {Colors.PRIMARY_BLUE_DARK});
            }}
        """)


class HoverPlotWidget(PlotWidget):
    """Custom PlotWidget that shows hover tooltips"""
    
    # Signal emitted when reset view button is clicked
    reset_view_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_label = None
        self.ping_data = []
        self.time_data = []
        self.start_time = None
        
        self.setMouseTracking(True)      
        self.create_hover_label()  
        self.create_reset_button()        
        self._setup_styling()
        
    def _setup_styling(self):
        """Setup the graph appearance"""
        self.setBackground(Colors.PRIMARY_BG)
        self.setLabel('left', 'Ping Time', units='ms', 
                     color=Colors.PRIMARY_TEXT, size='10pt')
        self.setLabel('bottom', 'Time', 
                     color=Colors.PRIMARY_TEXT, size='10pt')
        self.setTitle('Ping Response Time (Hover over points for details)', 
                     color=Colors.PRIMARY_TEXT, size='12pt')
        
        # Customize grid
        self.showGrid(x=True, y=True, alpha=0.3)
        
        # Set axis colors
        left_axis = self.getAxis('left')
        left_axis.setPen(color=Colors.SECONDARY_BORDER)
        left_axis.setTextPen(color=Colors.PRIMARY_TEXT)
        
        bottom_axis = self.getAxis('bottom')
        bottom_axis.setPen(color=Colors.SECONDARY_BORDER)
        bottom_axis.setTextPen(color=Colors.PRIMARY_TEXT)
        
    def create_hover_label(self):
        """Create the hover tooltip label"""
        self.hover_label = TextItem("", anchor=(0, 1), color='white')
        self.hover_label.setFont(QFont("Segoe UI", 9))
        self.hover_label.setHtml(f"""
            <div style='background: rgba(42, 42, 42, 0.9); 
                        border: 1px solid {Colors.TERTIARY_BORDER}; 
                        border-radius: 4px; 
                        padding: 8px; 
                        color: white;'>
                <b>Hover over a point</b>
            </div>
        """)
        self.addItem(self.hover_label)
        self.hover_label.hide()
        
    def create_reset_button(self):
        """Create the reset view button in the bottom left corner"""
        self.reset_button = ResetViewButton(self)
        self.reset_button.clicked.connect(self.on_reset_button_clicked)
        
        # Position the button in the bottom left corner
        self.position_reset_button()
        
    def position_reset_button(self):
        """Position the reset button in the bottom left corner"""
        # Position button with some margin from the edges
        margin = 10
        self.reset_button.move(margin, self.height() - self.reset_button.height() - margin)
        
    def resizeEvent(self, event):
        """Handle resize events to reposition the reset button"""
        super().resizeEvent(event)
        if hasattr(self, 'reset_button'):
            self.position_reset_button()
            
    def on_reset_button_clicked(self):
        """Handle reset button click"""
        self.reset_view_requested.emit()
        
    def update_data(self, time_data, ping_data, start_time):
        """Update the data arrays for hover functionality"""
        self.time_data = list(time_data)
        self.ping_data = list(ping_data)
        self.start_time = start_time
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events to show hover tooltips"""
        super().mouseMoveEvent(event)
        
        if len(self.ping_data) == 0 or len(self.time_data) == 0:
            self.hover_label.hide()
            return
            
        # Get mouse position in plot coordinates
        pos = event.position()
        mouse_point = self.getViewBox().mapSceneToView(pos)
        
        # Find the closest data point
        if len(self.time_data) > 0:
            time_array = np.array(self.time_data)
            ping_array = np.array(self.ping_data)
            
            # Find closest point by time
            time_distances = np.abs(time_array - mouse_point.x())
            closest_idx = np.argmin(time_distances)
            
            # Check if we're close enough to show tooltip
            view_range = self.getViewBox().viewRange()
            x_range = view_range[0][1] - view_range[0][0]
            y_range = view_range[1][1] - view_range[1][0]
            
            # Define "close enough" as 5% of the current view range
            x_threshold = x_range * 0.05
            y_threshold = y_range * 0.05
            
            closest_time = time_array[closest_idx]
            closest_ping = ping_array[closest_idx]
            
            time_diff = abs(closest_time - mouse_point.x())
            ping_diff = abs(closest_ping - mouse_point.y())
            
            if time_diff <= x_threshold and ping_diff <= y_threshold:
                # Show tooltip
                self.show_hover_info(closest_time, closest_ping, pos)
            else:
                self.hover_label.hide()
        else:
            self.hover_label.hide()
            
    def show_hover_info(self, time_seconds, ping_ms, screen_pos):
        """Show hover information for a specific point"""
        # Format the time
        if self.start_time:
            actual_time = self.start_time + timedelta(seconds=time_seconds)
            time_str = actual_time.strftime("%H:%M:%S")
        else:
            time_str = f"{time_seconds:.1f}s"
            
        # Create tooltip content
        html_content = f"""
            <div style='background: rgba(42, 42, 42, 0.95); 
                        border: 1px solid {Colors.PRIMARY_BLUE}; 
                        border-radius: 6px; 
                        padding: 10px; 
                        color: white;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.3);'>
                <div style='color: {Colors.PRIMARY_BLUE}; font-weight: bold; margin-bottom: 4px;'>
                    📊 Ping Data
                </div>
                <div style='margin-bottom: 2px;'>
                    <span style='color: {Colors.SECONDARY_TEXT};'>Time:</span> 
                    <span style='color: {Colors.PRIMARY_TEXT}; font-weight: 500;'>{time_str}</span>
                </div>
                <div>
                    <span style='color: {Colors.SECONDARY_TEXT};'>Ping:</span> 
                    <span style='color: {Colors.SUCCESS}; font-weight: bold; font-size: 11pt;'>{ping_ms:.1f} ms</span>
                </div>
            </div>
        """
        
        self.hover_label.setHtml(html_content)
        
        # Position the tooltip near the mouse, but keep it in bounds
        plot_pos = self.getViewBox().mapSceneToView(screen_pos)
        
        # Add small offset so tooltip doesn't block the point
        offset_x = 0.02 * (self.getViewBox().viewRange()[0][1] - self.getViewBox().viewRange()[0][0])
        offset_y = 0.02 * (self.getViewBox().viewRange()[1][1] - self.getViewBox().viewRange()[1][0])
        
        self.hover_label.setPos(plot_pos.x() + offset_x, plot_pos.y() + offset_y)
        self.hover_label.show()
        
    def leaveEvent(self, event):
        """Hide tooltip when mouse leaves the widget"""
        super().leaveEvent(event)
        if self.hover_label:
            self.hover_label.hide()
    
    def create_plot_line(self):
        """Create the main plot line for ping data"""
        plot_line = self.plot([], [], 
                             pen=pg.mkPen(color=Colors.PRIMARY_BLUE, width=2),
                             symbol='o', 
                             symbolBrush=Colors.PRIMARY_BLUE,
                             symbolSize=6,
                             symbolPen=pg.mkPen(color=Colors.PRIMARY_TEXT, width=1))
        return plot_line