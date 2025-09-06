import sys
import subprocess
import platform
import re
import threading
import time
import csv
import ctypes
from datetime import datetime, timedelta
from collections import deque
if platform.system() == "Windows":
    import ctypes

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox, QLabel, 
                             QFrame, QGridLayout, QSizePolicy, QSpacerItem, QGraphicsOpacityEffect,
                             QCheckBox, QGroupBox, QFileDialog, QMessageBox, QDialog, QDialogButtonBox)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import numpy as np


class NetworkTester(QObject):
    test_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self):
        super().__init__()
        
    def test_connection(self):
        """Test network connectivity to multiple reliable hosts"""
        thread = threading.Thread(target=self._test_connection_thread, daemon=True)
        thread.start()
        
    def _test_connection_thread(self):
        """Test connectivity in a separate thread"""
        test_hosts = ["8.8.8.8", "1.1.1.1", "google.com"]  # Google DNS, Cloudflare DNS, Google
        
        for host in test_hosts:
            if self._ping_host(host):
                self.test_completed.emit(True, f"✓ Network connection is active (tested with {host})")
                return
                
        self.test_completed.emit(False, "✗ No network connection detected")
        
    def _ping_host(self, host):
        """Quick ping test to a single host"""
        try:
            system = platform.system().lower()
            if system == "windows":
                cmd = ["ping", "-n", "1", "-w", "3000", host]  # 3 second timeout
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                cmd = ["ping", "-c", "1", "-W", "3", host]  # 3 second timeout
                startupinfo = None
                creationflags = 0
                
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=5,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            return result.returncode == 0
        except Exception:
            return False


class PingWorker(QObject):
    ping_result = pyqtSignal(float)
    ping_failed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.domain = ""
        self.interval = 1.0
        
    def start_pinging(self, domain, interval):
        self.domain = domain
        self.interval = interval
        self.running = True
        thread = threading.Thread(target=self._ping_loop, daemon=True)
        thread.start()
        
    def stop_pinging(self):
        self.running = False
        
    def _ping_loop(self):
        while self.running:
            ping_time = self._ping_host(self.domain)
            if ping_time is not None:
                self.ping_result.emit(ping_time)
            else:
                self.ping_failed.emit()
            time.sleep(self.interval)
            
    def _ping_host(self, host):
        try:
            system = platform.system().lower()
            if system == "windows":
                cmd = ["ping", "-n", "1", host]
                # Hide console window on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                cmd = ["ping", "-c", "1", host]
                startupinfo = None
                creationflags = 0
                
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=5,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            if result.returncode == 0:
                output = result.stdout
                if system == "windows":
                    match = re.search(r'time[<=](\d+)ms', output)
                else:
                    match = re.search(r'time=(\d+\.?\d*)\s*ms', output)
                
                if match:
                    return float(match.group(1))
            return None
        except Exception:
            return None


class ModernButton(QPushButton):
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.is_danger_mode = False
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        
        # Create opacity effect for smooth transitions
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        self._setup_style()
        
    def _setup_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #4A90E2, stop: 1 #357ABD);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #5BA0F2, stop: 1 #4A90E2);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #357ABD, stop: 1 #2E6BA8);
                }
                QPushButton:disabled {
                    background: #444444;
                    color: #888888;
                }
            """)
        elif self.is_danger_mode:
            # Red styling for danger state
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #E74C3C, stop: 1 #C0392B);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #EC7063, stop: 1 #E74C3C);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #C0392B, stop: 1 #A93226);
                }
                QPushButton:disabled {
                    background: #444444;
                    color: #888888;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #3A3A3A;
                    color: #E0E0E0;
                    border: 1px solid #555555;
                    border-radius: 8px;
                    font-weight: 500;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #464646;
                    border-color: #666666;
                }
                QPushButton:pressed {
                    background: #2E2E2E;
                }
                QPushButton:disabled {
                    background: #2A2A2A;
                    color: #666666;
                    border-color: #444444;
                }
            """)
    
    def set_danger_mode(self, danger):
        """Switch between normal and danger styling"""
        if self.is_danger_mode != danger:
            self.is_danger_mode = danger
            self._setup_style()
    
    def animate_state_change(self, enabled):
        """Animate the button state change"""
        # Create fade out animation
        fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_out.setDuration(150)
        fade_out.setStartValue(self.opacity_effect.opacity())
        fade_out.setEndValue(0.4)
        fade_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Create fade in animation
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_in.setDuration(150)
        fade_in.setStartValue(0.4)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Define what happens after fade out
        def on_fade_out_finished():
            self.setEnabled(enabled)
            fade_in.start()
        
        # Connect animations
        fade_out.finished.connect(on_fade_out_finished)
        
        # Start the animation sequence
        fade_out.start()
        
        # Store references to prevent garbage collection
        self._fade_out_anim = fade_out
        self._fade_in_anim = fade_in


class CompactButton(QPushButton):
    """Smaller button for header area"""
    def __init__(self, text, style="secondary"):
        super().__init__(text)
        self.style_type = style
        self.setMinimumHeight(32)
        self.setMaximumHeight(32)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self._setup_style()
        
    def _setup_style(self):
        if self.style_type == "success":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #28A745, stop: 1 #1E7E34);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #34CE57, stop: 1 #28A745);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #1E7E34, stop: 1 #155724);
                }
                QPushButton:disabled {
                    background: #444444;
                    color: #888888;
                }
            """)
        elif self.style_type == "info":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #17A2B8, stop: 1 #138496);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #20C0DB, stop: 1 #17A2B8);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #138496, stop: 1 #0C6674);
                }
                QPushButton:disabled {
                    background: #444444;
                    color: #888888;
                }
            """)
        elif self.style_type == "settings":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #6F42C1, stop: 1 #5A31A5);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #8A5CF5, stop: 1 #6F42C1);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 #5A31A5, stop: 1 #4C2A91);
                }
                QPushButton:disabled {
                    background: #444444;
                    color: #888888;
                }
            """)
        else:  # secondary
            self.setStyleSheet("""
                QPushButton {
                    background: #3A3A3A;
                    color: #E0E0E0;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    font-weight: 500;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: #464646;
                    border-color: #666666;
                }
                QPushButton:pressed {
                    background: #2E2E2E;
                }
                QPushButton:disabled {
                    background: #2A2A2A;
                    color: #666666;
                    border-color: #444444;
                }
            """)


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QLineEdit {
                background: #2A2A2A;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: #E0E0E0;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #555555;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)


class ModernSpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QSpinBox {
                background: #2A2A2A;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: #E0E0E0;
            }
            QSpinBox:focus {
                border-color: #4A90E2;
                outline: none;
            }
            QSpinBox:hover {
                border-color: #555555;
            }
        """)


class ModernDoubleSpinBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QDoubleSpinBox {
                background: #2A2A2A;
                border: 2px solid #444444;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: #E0E0E0;
            }
            QDoubleSpinBox:focus {
                border-color: #4A90E2;
                outline: none;
            }
            QDoubleSpinBox:hover {
                border-color: #555555;
            }
        """)


class ModernCheckBox(QCheckBox):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QCheckBox {
                color: #E0E0E0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #555555;
                background: #2A2A2A;
            }
            QCheckBox::indicator:checked {
                background: #4A90E2;
                border-color: #4A90E2;
            }
            QCheckBox::indicator:checked:hover {
                background: #5BA0F2;
                border-color: #5BA0F2;
            }
            QCheckBox::indicator:hover {
                border-color: #666666;
                background: #333333;
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)


class StatCard(QFrame):
    def __init__(self, title, value="0 ms", color="#4A90E2"):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        title_label.setStyleSheet("color: #AAAAAA;")
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
    def update_value(self, value):
        self.value_label.setText(value)


class SettingsDialog(QDialog):
    """Settings dialog for configuring display options"""
    
    def __init__(self, parent=None, show_advanced_stats=False, show_graph_options=False):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Apply dark theme to dialog
        self.setStyleSheet("""
            QDialog {
                background: #1E1E1E;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 10pt;
            }
            QGroupBox {
                color: #E0E0E0;
                font-weight: bold;
                border: 2px solid #444444;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #4A90E2;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Display Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #4A90E2; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Statistics Group
        stats_group = QGroupBox("Statistics Display")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(15)
        
        self.show_advanced_stats_checkbox = ModernCheckBox("Show Advanced Statistics")
        self.show_advanced_stats_checkbox.setChecked(show_advanced_stats)
        self.show_advanced_stats_checkbox.setToolTip("Display additional statistics: Min/Max ping, Jitter, and Connection Quality")
        stats_layout.addWidget(self.show_advanced_stats_checkbox)
        
        # Advanced stats description
        advanced_desc = QLabel("Advanced statistics include minimum/maximum ping times, jitter (variance), and connection quality indicators.")
        advanced_desc.setWordWrap(True)
        advanced_desc.setStyleSheet("color: #AAAAAA; font-size: 9pt; margin-left: 25px;")
        stats_layout.addWidget(advanced_desc)
        
        layout.addWidget(stats_group)
        
        # Graph Options Group
        graph_group = QGroupBox("Graph View Options")
        graph_layout = QVBoxLayout(graph_group)
        graph_layout.setSpacing(15)
        
        self.show_graph_options_checkbox = ModernCheckBox("Show Graph View Controls")
        self.show_graph_options_checkbox.setChecked(show_graph_options)
        self.show_graph_options_checkbox.setToolTip("Display controls for follow mode and view reset options")
        graph_layout.addWidget(self.show_graph_options_checkbox)
        
        # Graph options description
        graph_desc = QLabel("Graph view controls allow you to enable follow mode (scrolling window) and provide manual view reset options.")
        graph_desc.setWordWrap(True)
        graph_desc.setStyleSheet("color: #AAAAAA; font-size: 9pt; margin-left: 25px;")
        graph_layout.addWidget(graph_desc)
        
        layout.addWidget(graph_group)
        
        # Spacer
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background: #3A3A3A;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: 6px;
                font-weight: 500;
                padding: 8px 16px;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background: #464646;
                border-color: #666666;
            }
            QDialogButtonBox QPushButton:pressed {
                background: #2E2E2E;
            }
            QDialogButtonBox QPushButton[text="OK"] {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #4A90E2, stop: 1 #357ABD);
                border: none;
            }
            QDialogButtonBox QPushButton[text="OK"]:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #5BA0F2, stop: 1 #4A90E2);
            }
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_settings(self):
        """Return the current settings"""
        return {
            'show_advanced_stats': self.show_advanced_stats_checkbox.isChecked(),
            'show_graph_options': self.show_graph_options_checkbox.isChecked()
        }


class HoverPlotWidget(PlotWidget):
    """Custom PlotWidget that shows hover tooltips"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_label = None
        self.ping_data = []
        self.time_data = []
        self.start_time = None
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Create hover label
        self.create_hover_label()
        
    def create_hover_label(self):
        """Create the hover tooltip label"""
        self.hover_label = pg.TextItem("", anchor=(0, 1), color='white')
        self.hover_label.setFont(QFont("Segoe UI", 9))
        self.hover_label.setHtml("""
            <div style='background: rgba(42, 42, 42, 0.9); 
                        border: 1px solid #666; 
                        border-radius: 4px; 
                        padding: 8px; 
                        color: white;'>
                <b>Hover over a point</b>
            </div>
        """)
        self.addItem(self.hover_label)
        self.hover_label.hide()
        
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
                        border: 1px solid #4A90E2; 
                        border-radius: 6px; 
                        padding: 10px; 
                        color: white;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.3);'>
                <div style='color: #4A90E2; font-weight: bold; margin-bottom: 4px;'>
                    📊 Ping Data
                </div>
                <div style='margin-bottom: 2px;'>
                    <span style='color: #AAAAAA;'>Time:</span> 
                    <span style='color: #E0E0E0; font-weight: 500;'>{time_str}</span>
                </div>
                <div>
                    <span style='color: #AAAAAA;'>Ping:</span> 
                    <span style='color: #28A745; font-weight: bold; font-size: 11pt;'>{ping_ms:.1f} ms</span>
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


class PingPoller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ping Poller")
        self.setGeometry(100, 100, 1200, 800)   
        
        # Data storage
        self.ping_times = deque(maxlen=1000)
        self.timestamps = deque(maxlen=1000)
        self.start_time = None
        self.is_running = False
        
        # Statistics
        self.ping_count = 0
        self.failed_count = 0
        self.total_ping_time = 0
        self.min_ping = float('inf')
        self.max_ping = 0
        self.recent_pings = deque(maxlen=100)  # For jitter calculation
        
        # View tracking
        self.auto_range_enabled = True
        self.follow_mode_enabled = False
        self.follow_window_seconds = 10
        self.original_view_range = None
        
        # Settings - both default to False
        self.show_advanced_stats = False
        self.show_graph_options = False
        
        # Worker threads
        self.ping_worker = PingWorker()
        self.ping_worker.ping_result.connect(self.on_ping_result)
        self.ping_worker.ping_failed.connect(self.on_ping_failed)
        
        self.network_tester = NetworkTester()
        self.network_tester.test_completed.connect(self.on_network_test_completed)
        
        self._setup_ui()
        self._setup_graph()
        self._apply_theme()
        self._update_ui_visibility()
        
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and utility buttons
        header_layout = QHBoxLayout()
        
        title = QLabel("Ping Poller")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #E0E0E0; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
        # Add spacing between title and buttons
        header_layout.addSpacing(20)
        
        # Network test button
        self.network_test_button = CompactButton("🔗 Test Network", "success")
        self.network_test_button.clicked.connect(self.test_network_connection)
        self.network_test_button.setToolTip("Test basic network connectivity")
        header_layout.addWidget(self.network_test_button)
        
        # Export CSV button
        self.export_csv_button = CompactButton("📊 Export CSV", "info")
        self.export_csv_button.clicked.connect(self.export_to_csv)
        self.export_csv_button.setToolTip("Export ping data to CSV file")
        self.export_csv_button.setEnabled(False)  # Disabled until we have data
        header_layout.addWidget(self.export_csv_button)
        
        header_layout.addStretch()
        
        # Settings button
        self.settings_button = CompactButton("⚙️ Settings", "settings")
        self.settings_button.clicked.connect(self.show_settings)
        self.settings_button.setToolTip("Configure display options")
        header_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(header_layout)
        
        # Controls section
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        controls_layout = QGridLayout(controls_frame)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        
        # Domain input
        domain_label = QLabel("Target Domain/IP:")
        domain_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        domain_label.setStyleSheet("color: #AAAAAA;")
        
        self.domain_input = ModernLineEdit("google.com")
        self.domain_input.setText("google.com")
        
        # Interval input
        interval_label = QLabel("Ping Interval (seconds):")
        interval_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        interval_label.setStyleSheet("color: #AAAAAA;")
        
        self.interval_input = ModernDoubleSpinBox()
        self.interval_input.setRange(0.1, 60.0)
        self.interval_input.setValue(1.0)
        self.interval_input.setDecimals(1)
        self.interval_input.setSingleStep(0.1)
        self.interval_input.setSuffix(" sec")
        self.interval_input.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        
        # Duration input
        duration_label = QLabel("Test Duration (seconds):")
        duration_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        duration_label.setStyleSheet("color: #AAAAAA;")
        
        self.duration_input = ModernSpinBox()
        self.duration_input.setRange(10, 3600)
        self.duration_input.setValue(60)
        self.duration_input.setSuffix(" sec")
        self.duration_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        
        # Buttons with enhanced styling
        self.start_button = ModernButton("Start Test", primary=True)
        self.start_button.clicked.connect(self.start_test)
        
        self.stop_button = ModernButton("Stop Test")
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setEnabled(False)
        
        # Layout controls (first row)
        controls_layout.addWidget(domain_label, 0, 0)
        controls_layout.addWidget(self.domain_input, 0, 1)
        controls_layout.addWidget(interval_label, 0, 2)
        controls_layout.addWidget(self.interval_input, 0, 3)
        
        # Second row
        controls_layout.addWidget(duration_label, 1, 0)
        controls_layout.addWidget(self.duration_input, 1, 1)
        controls_layout.addWidget(self.start_button, 1, 2)
        controls_layout.addWidget(self.stop_button, 1, 3)
        
        main_layout.addWidget(controls_frame)
        
        # Graph Options section - initially hidden
        self.graph_options_frame = QFrame()
        self.graph_options_frame.setStyleSheet("""
            QFrame {
                background: #2A2A2A;
                border: 1px solid #444444;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        graph_options_layout = QHBoxLayout(self.graph_options_frame)
        graph_options_layout.setContentsMargins(20, 15, 20, 15)
        
        # Graph options label
        graph_options_label = QLabel("Graph View:")
        graph_options_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        graph_options_label.setStyleSheet("color: #AAAAAA;")
        graph_options_layout.addWidget(graph_options_label)
        
        # Follow mode checkbox
        self.follow_mode_checkbox = ModernCheckBox("Follow Mode (Last 10s)")
        self.follow_mode_checkbox.setToolTip("Show only the last 10 seconds of data in a scrolling window")
        self.follow_mode_checkbox.stateChanged.connect(self.on_follow_mode_changed)
        graph_options_layout.addWidget(self.follow_mode_checkbox)
        
        # Follow window duration
        follow_window_label = QLabel("Window:")
        follow_window_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        follow_window_label.setStyleSheet("color: #AAAAAA;")
        graph_options_layout.addWidget(follow_window_label)
        
        self.follow_window_input = ModernSpinBox()
        self.follow_window_input.setRange(5, 60)
        self.follow_window_input.setValue(10)
        self.follow_window_input.setSuffix(" sec")
        self.follow_window_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.follow_window_input.setMaximumWidth(100)
        self.follow_window_input.setToolTip("Duration of the follow window in seconds")
        self.follow_window_input.valueChanged.connect(self.on_follow_window_changed)
        self.follow_window_input.setEnabled(False)  # Disabled until follow mode is enabled
        graph_options_layout.addWidget(self.follow_window_input)
        
        graph_options_layout.addStretch()
        
        # Reset view button
        self.reset_view_button = CompactButton("Reset View", "secondary")
        self.reset_view_button.clicked.connect(self.reset_view)
        self.reset_view_button.setEnabled(False)
        self.reset_view_button.setToolTip("Reset graph to show all data with auto-scaling")
        graph_options_layout.addWidget(self.reset_view_button)
        
        main_layout.addWidget(self.graph_options_frame)
        
        # Basic Statistics cards (always visible)
        self.basic_stats_layout = QHBoxLayout()
        self.current_ping_card = StatCard("Current Ping", "0 ms", "#28A745")
        self.avg_ping_card = StatCard("Average Ping", "0 ms", "#4A90E2")
        self.packet_loss_card = StatCard("Packet Loss", "0%", "#DC3545")
        self.ping_count_card = StatCard("Ping Count", "0", "#6F42C1")
        
        self.basic_stats_layout.addWidget(self.current_ping_card)
        self.basic_stats_layout.addWidget(self.avg_ping_card)
        self.basic_stats_layout.addWidget(self.packet_loss_card)
        self.basic_stats_layout.addWidget(self.ping_count_card)
        
        main_layout.addLayout(self.basic_stats_layout)
        
        # Advanced Statistics section - initially hidden
        self.advanced_stats_layout = QHBoxLayout()
        self.min_ping_card = StatCard("Min Ping", "0 ms", "#17A2B8")
        self.max_ping_card = StatCard("Max Ping", "0 ms", "#FD7E14")
        self.jitter_card = StatCard("Jitter", "0 ms", "#E83E8C")
        self.status_card = StatCard("Ping Quality", "Ready", "#6C757D")
        
        self.advanced_stats_layout.addWidget(self.min_ping_card)
        self.advanced_stats_layout.addWidget(self.max_ping_card)
        self.advanced_stats_layout.addWidget(self.jitter_card)
        self.advanced_stats_layout.addWidget(self.status_card)
        
        main_layout.addLayout(self.advanced_stats_layout)
        
        # Graph container
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # Graph with hover functionality
        self.graph_widget = HoverPlotWidget()
        self.graph_widget.setMinimumHeight(400)
        
        graph_layout.addWidget(self.graph_widget)
        
        main_layout.addWidget(graph_container)
        
        # Timer for auto-stop
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.stop_test)
    
    def show_settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self, self.show_advanced_stats, self.show_graph_options)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.show_advanced_stats = settings['show_advanced_stats']
            self.show_graph_options = settings['show_graph_options']
            self._update_ui_visibility()
    
    def _update_ui_visibility(self):
        """Update UI element visibility based on settings"""
        # Show/hide advanced statistics
        for i in range(self.advanced_stats_layout.count()):
            item = self.advanced_stats_layout.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(self.show_advanced_stats)
        
        # Show/hide graph options
        self.graph_options_frame.setVisible(self.show_graph_options)
        
    def on_follow_mode_changed(self, state):
        """Handle follow mode checkbox changes"""
        self.follow_mode_enabled = state == Qt.CheckState.Checked.value
        self.follow_window_input.setEnabled(self.follow_mode_enabled)
        
        if self.follow_mode_enabled:
            # Disable auto-range when follow mode is enabled
            self.auto_range_enabled = False
            self.follow_window_seconds = self.follow_window_input.value()
            # Update the checkbox label to show current window size
            self.follow_mode_checkbox.setText(f"Follow Mode (Last {self.follow_window_seconds}s)")
        else:
            # Re-enable auto-range when follow mode is disabled
            self.auto_range_enabled = True
            self.follow_mode_checkbox.setText("Follow Mode (Last 10s)")
            
        # Update graph view immediately if we have data
        if len(self.timestamps) > 0:
            self.update_graph_view()
            
    def on_follow_window_changed(self, value):
        """Handle follow window duration changes"""
        self.follow_window_seconds = value
        if self.follow_mode_enabled:
            # Update the checkbox label
            self.follow_mode_checkbox.setText(f"Follow Mode (Last {value}s)")
            # Update graph view immediately if we have data
            if len(self.timestamps) > 0:
                self.update_graph_view()
        
    def _setup_graph(self):
        self.graph_widget.setBackground('#1E1E1E')
        self.graph_widget.setLabel('left', 'Ping Time', units='ms', 
                                  color='#E0E0E0', size='10pt')
        self.graph_widget.setLabel('bottom', 'Time', 
                                  color='#E0E0E0', size='10pt')
        self.graph_widget.setTitle('Ping Response Time (Hover over points for details)', 
                                  color='#E0E0E0', size='12pt')
        
        # Customize grid
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set axis colors
        axis = self.graph_widget.getAxis('left')
        axis.setPen(color='#555555')
        axis.setTextPen(color='#E0E0E0')
        
        axis = self.graph_widget.getAxis('bottom')
        axis.setPen(color='#555555')
        axis.setTextPen(color='#E0E0E0')
        
        # Create plot line with larger symbols for better hovering
        self.plot_line = self.graph_widget.plot([], [], 
                                               pen=pg.mkPen(color='#4A90E2', width=2),
                                               symbol='o', 
                                               symbolBrush='#4A90E2',
                                               symbolSize=6,
                                               symbolPen=pg.mkPen(color='#E0E0E0', width=1))
        
        # Connect view range changed signal to detect manual zoom/pan
        self.graph_widget.sigRangeChanged.connect(self.on_range_changed)
        
    def on_range_changed(self):
        """Called when the graph view range changes (zoom/pan)"""
        if not self.follow_mode_enabled and self.is_running and len(self.timestamps) > 0:
            # Check if we're still in auto-range mode (only when not in follow mode)
            view_box = self.graph_widget.getViewBox()
            current_range = view_box.viewRange()
            
            # Calculate what the auto range should be
            if len(self.timestamps) > 1:
                x_range = [min(self.timestamps), max(self.timestamps)]
                x_padding = (x_range[1] - x_range[0]) * 0.05 if x_range[1] > x_range[0] else 1
                expected_x_range = [x_range[0] - x_padding, x_range[1] + x_padding]
            else:
                expected_x_range = [-1, 1]
                
            # Compare current range with expected auto range (with tolerance)
            tolerance = 0.1  # 10% tolerance
            x_diff = abs(current_range[0][1] - expected_x_range[1])
            x_total = expected_x_range[1] - expected_x_range[0] if expected_x_range[1] > expected_x_range[0] else 1
            
            if x_diff > x_total * tolerance:
                # User has manually changed the view
                self.auto_range_enabled = False
                if self.show_graph_options:
                    self.reset_view_button.setEnabled(True)
            else:
                # We're still in auto range
                self.auto_range_enabled = True
                if self.show_graph_options:
                    self.reset_view_button.setEnabled(False)
        
    def reset_view(self):
        """Reset the graph view to auto-range mode"""
        self.auto_range_enabled = True
        self.follow_mode_enabled = False
        
        # Update UI
        if self.show_graph_options:
            self.follow_mode_checkbox.setChecked(False)
            self.follow_window_input.setEnabled(False)
            self.reset_view_button.setEnabled(False)
        
        # Reset graph view
        if len(self.timestamps) > 0:
            self.graph_widget.enableAutoRange()
        else:
            self.graph_widget.setRange(xRange=[-1, 1], yRange=[0, 100])
            
    def update_graph_view(self):
        """Update the graph view based on current mode"""
        if not len(self.timestamps):
            return
            
        if self.follow_mode_enabled:
            # Follow mode: show only the last N seconds
            current_time = max(self.timestamps)
            window_start = current_time - self.follow_window_seconds
            
            # Find data points within the window
            visible_times = []
            visible_pings = []
            
            for i, timestamp in enumerate(self.timestamps):
                if timestamp >= window_start:
                    visible_times.append(timestamp)
                    visible_pings.append(self.ping_times[i])
            
            if visible_times:
                # Set the view range to show the follow window
                x_range = [window_start, current_time]
                
                # Calculate Y range with some padding
                if visible_pings:
                    y_min = min(visible_pings)
                    y_max = max(visible_pings)
                    y_padding = max((y_max - y_min) * 0.1, 10)  # At least 10ms padding
                    y_range = [max(0, y_min - y_padding), y_max + y_padding]
                else:
                    y_range = [0, 100]
                
                # Disable auto range and set manual range
                self.graph_widget.setRange(xRange=x_range, yRange=y_range, padding=0)
                
        elif self.auto_range_enabled:
            # Auto-range mode: show all data
            self.graph_widget.enableAutoRange()
        
    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #1E1E1E;
            }
            QLabel {
                color: #E0E0E0;
            }
        """)
        
    def test_network_connection(self):
        """Test network connectivity"""
        # Disable the button during testing
        self.network_test_button.setEnabled(False)
        self.network_test_button.setText("🔄 Testing...")
        
        # Start the network test
        self.network_tester.test_connection()
    
    def on_network_test_completed(self, success, message):
        """Handle network test completion"""
        # Re-enable the button
        self.network_test_button.setEnabled(True)
        self.network_test_button.setText("🔗 Test Network")
        
        # Show result message
        if success:
            QMessageBox.information(self, "Network Test", message)
        else:
            QMessageBox.warning(self, "Network Test", message)
    
    def export_to_csv(self):
        """Export ping data to CSV file"""
        if len(self.ping_times) == 0:
            QMessageBox.information(self, "Export CSV", "No ping data to export. Run a test first.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Ping Data to CSV",
            f"ping_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Timestamp', 'Elapsed_Time_Seconds', 'Ping_Time_MS', 
                    'Target_Host', 'Test_Start_Time'
                ])
                
                # Write data
                target_host = self.domain_input.text().strip() if self.domain_input.text().strip() else "Unknown"
                start_time_str = self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else "Unknown"
                
                for i, (elapsed_time, ping_time) in enumerate(zip(self.timestamps, self.ping_times)):
                    if self.start_time:
                        actual_timestamp = (self.start_time + timedelta(seconds=elapsed_time)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    else:
                        actual_timestamp = f"T+{elapsed_time:.3f}s"
                    
                    writer.writerow([
                        actual_timestamp,
                        f"{elapsed_time:.3f}",
                        f"{ping_time:.1f}",
                        target_host,
                        start_time_str
                    ])
                
                # Write summary statistics
                writer.writerow([])  # Empty row
                writer.writerow(['=== SUMMARY STATISTICS ==='])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Pings', str(self.ping_count)])
                writer.writerow(['Failed Pings', str(self.failed_count)])
                writer.writerow(['Packet Loss %', f"{(self.failed_count / (self.ping_count + self.failed_count) * 100) if (self.ping_count + self.failed_count) > 0 else 0:.1f}%"])
                writer.writerow(['Average Ping (ms)', f"{(self.total_ping_time / self.ping_count) if self.ping_count > 0 else 0:.1f}"])
                writer.writerow(['Minimum Ping (ms)', f"{self.min_ping if self.min_ping != float('inf') else 0:.1f}"])
                writer.writerow(['Maximum Ping (ms)', f"{self.max_ping:.1f}"])
                
                if len(self.recent_pings) >= 2:
                    jitter = np.std(np.array(self.recent_pings))
                    writer.writerow(['Jitter (ms)', f"{jitter:.1f}"])
                
                writer.writerow(['Test Duration (seconds)', f"{max(self.timestamps) if self.timestamps else 0:.1f}"])
                writer.writerow(['Ping Interval (seconds)', f"{self.interval_input.value():.1f}"])
            
            QMessageBox.information(self, "Export Complete", f"Ping data exported successfully to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")
        
    def start_test(self):
        domain = self.domain_input.text().strip()
        if not domain:
            return
            
        duration = self.duration_input.value()
        interval = self.interval_input.value()
        
        # Reset data
        self.clear_data()
        
        # Enable export button now that we'll have data
        self.export_csv_button.setEnabled(True)
        
        # Reset view states
        if not self.follow_mode_enabled:
            self.auto_range_enabled = True
            if self.show_graph_options:
                self.reset_view_button.setEnabled(False)
        
        # Update UI state with animations
        self.is_running = True
        self.start_time = datetime.now()
        
        # Update status
        if self.show_advanced_stats:
            self.status_card.update_value("Ready")
            self.status_card.value_label.setStyleSheet("color: #6C757D;")  # Gray for ready
        
        # Switch stop button to danger mode
        self.stop_button.set_danger_mode(True)
        
        # Animate button state changes
        self.start_button.animate_state_change(False)
        self.stop_button.animate_state_change(True)
        
        # Start ping worker
        self.ping_worker.start_pinging(domain, interval)
        
        # Set auto-stop timer
        self.test_timer.start(duration * 1000)
        
    def stop_test(self):
        self.is_running = False
        self.ping_worker.stop_pinging()
        self.test_timer.stop()
        
        # Update status
        if self.show_advanced_stats:
            self.status_card.update_value("Ready")
            self.status_card.value_label.setStyleSheet("color: #6C757D;")  # Gray for ready
        
        # Remove danger mode
        self.stop_button.set_danger_mode(False)
        
        # Update UI state with animations
        self.start_button.animate_state_change(True)
        self.stop_button.animate_state_change(False)
        
    def clear_data(self):
        self.ping_times.clear()
        self.timestamps.clear()
        self.ping_count = 0
        self.failed_count = 0
        self.total_ping_time = 0
        self.min_ping = float('inf')
        self.max_ping = 0
        self.recent_pings.clear()
        
        # Update graph
        self.plot_line.setData([], [])
        
        # Clear hover data
        self.graph_widget.update_data([], [], None)
        
        # Update statistics
        self.current_ping_card.update_value("0 ms")
        self.avg_ping_card.update_value("0 ms")
        self.packet_loss_card.update_value("0%")
        self.ping_count_card.update_value("0")
        
        if self.show_advanced_stats:
            self.min_ping_card.update_value("0 ms")
            self.max_ping_card.update_value("0 ms")
            self.jitter_card.update_value("0 ms")
            self.status_card.update_value("Ready")
            self.status_card.value_label.setStyleSheet("color: #6C757D;")
        
        # Disable export button when no data
        self.export_csv_button.setEnabled(False)
        
    def on_ping_result(self, ping_time):
        if not self.is_running:
            return
            
        current_time = (datetime.now() - self.start_time).total_seconds()
        
        self.ping_times.append(ping_time)
        self.timestamps.append(current_time)
        self.ping_count += 1
        self.total_ping_time += ping_time
        self.recent_pings.append(ping_time)
        
        # Update min/max
        self.min_ping = min(self.min_ping, ping_time)
        self.max_ping = max(self.max_ping, ping_time)
        
        # Calculate jitter (standard deviation of recent pings)
        if len(self.recent_pings) >= 2:
            recent_array = np.array(self.recent_pings)
            jitter = np.std(recent_array)
        else:
            jitter = 0
        
        # Update graph
        self.plot_line.setData(list(self.timestamps), list(self.ping_times))
        
        # Update hover data
        self.graph_widget.update_data(self.timestamps, self.ping_times, self.start_time)
        
        # Update graph view based on current mode
        self.update_graph_view()
        
        # Update basic statistics (always visible)
        self.current_ping_card.update_value(f"{ping_time:.1f} ms")
        
        avg_ping = self.total_ping_time / self.ping_count
        self.avg_ping_card.update_value(f"{avg_ping:.1f} ms")
        
        total_attempts = self.ping_count + self.failed_count
        packet_loss = (self.failed_count / total_attempts * 100) if total_attempts > 0 else 0
        self.packet_loss_card.update_value(f"{packet_loss:.1f}%")
        
        self.ping_count_card.update_value(str(self.ping_count))
        
        # Update advanced statistics (only if enabled)
        if self.show_advanced_stats:
            self.min_ping_card.update_value(f"{self.min_ping:.1f} ms")
            self.max_ping_card.update_value(f"{self.max_ping:.1f} ms")
            self.jitter_card.update_value(f"{jitter:.1f} ms")
            
            # Update status with color coding based on ping quality
            if ping_time < 50:
                status_text = "Excellent"
                status_color = "#28A745"  # Green
            elif ping_time < 100:
                status_text = "Good"
                status_color = "#FFC107"  # Yellow
            elif ping_time < 200:
                status_text = "Fair"
                status_color = "#FD7E14"  # Orange
            else:
                status_text = "Poor"
                status_color = "#DC3545"  # Red
                
            self.status_card.update_value(status_text)
            self.status_card.value_label.setStyleSheet(f"color: {status_color};")
        
    def on_ping_failed(self):
        if not self.is_running:
            return
            
        self.failed_count += 1
        
        # Update packet loss
        total_attempts = self.ping_count + self.failed_count
        packet_loss = (self.failed_count / total_attempts * 100) if total_attempts > 0 else 0
        self.packet_loss_card.update_value(f"{packet_loss:.1f}%")
        
        # Update status to show connection issues (only if advanced stats enabled)
        if self.show_advanced_stats:
            self.status_card.update_value("Connection Issue")
            self.status_card.value_label.setStyleSheet("color: #DC3545;")  # Red for failed pings


def main():
     if platform.system() == "Windows":
        try:
            app_id = 'PingPoller.1.0.0'  # Change this to your preferred ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            # Silently fail if there are issues (e.g., on older Windows versions)
            pass
        
     app = QApplication(sys.argv)
     app.setApplicationName("Ping Poller") 
     app.setApplicationVersion("1.0.0")

     # Set application style
     app.setStyle('Fusion')
    
     app.setWindowIcon(QIcon('assets/icons/ping-poller.ico'))

     window = PingPoller()
     window.show()
     
     sys.exit(app.exec())


if __name__ == "__main__":
    main()