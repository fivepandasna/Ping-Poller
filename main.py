# main.py
"""
Main application file for Ping Poller - a network latency monitoring tool.
"""

import sys
import platform
import ctypes
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QFrame, QGridLayout, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QIcon
import pyqtgraph as pg
import numpy as np

# Local imports
from constants import Colors, AppConfig
from network_utils import NetworkTester, PingWorker
from ui_widgets import (ModernButton, CompactButton, ModernLineEdit, ModernSpinBox,
                       ModernDoubleSpinBox, ModernCheckBox, StatCard, SettingsDialog)
from graph_widget import HoverPlotWidget
from data_manager import PingDataManager


class PingPoller(QMainWindow):
    """Main application window for the Ping Poller"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(AppConfig.APP_NAME)
        self.setGeometry(AppConfig.MIN_WINDOW_POS_X, AppConfig.MIN_WINDOW_POS_Y, 
                        AppConfig.DEFAULT_WINDOW_WIDTH, AppConfig.DEFAULT_WINDOW_HEIGHT)
        
        # Data management
        self.data_manager = PingDataManager()
        self.is_running = False
        
        # View tracking
        self.auto_range_enabled = True
        self.follow_mode_enabled = False
        self.follow_window_seconds = AppConfig.DEFAULT_FOLLOW_WINDOW
        
        # Settings 
        self.show_advanced_stats = False
        self.show_graph_controls = False  # New setting for graph controls visibility
        
        # Worker threads
        self._setup_workers()
        
        # UI Setup
        self._setup_ui()
        self._setup_graph()
        self._apply_theme()
        self._update_ui_visibility()
        
        # Timer for auto-stop
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.stop_test)
    
    def _setup_workers(self):
        """Initialize network worker threads"""
        self.ping_worker = PingWorker()
        self.ping_worker.ping_result.connect(self.on_ping_result)
        self.ping_worker.ping_failed.connect(self.on_ping_failed)
        
        self.network_tester = NetworkTester()
        self.network_tester.test_completed.connect(self.on_network_test_completed)
    
    def _setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add all UI components
        self._create_header(main_layout)
        self._create_controls(main_layout)
        self._create_statistics_cards(main_layout)
        self._create_graph_container(main_layout)
    
    def _create_header(self, main_layout):
        """Create the application header with title and utility buttons"""
        header_layout = QHBoxLayout()
        
        title = QLabel(AppConfig.APP_NAME)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY_TEXT}; margin-bottom: 10px;")
        header_layout.addWidget(title)
        
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
        self.export_csv_button.setEnabled(False)
        header_layout.addWidget(self.export_csv_button)
        
        header_layout.addStretch()
        
        # Settings button
        self.settings_button = CompactButton("⚙️ Settings", "settings")
        self.settings_button.clicked.connect(self.show_settings)
        self.settings_button.setToolTip("Configure display options")
        header_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(header_layout)
    
    def _create_controls(self, main_layout):
        """Create the main control panel"""
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background: {Colors.SECONDARY_BG};
                border: 1px solid {Colors.PRIMARY_BORDER};
                border-radius: 12px;
                padding: 10px;
            }}
        """)
        controls_layout = QGridLayout(controls_frame)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        
        # Domain input
        domain_label = QLabel("Target Domain/IP:")
        domain_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        domain_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        
        self.domain_input = ModernLineEdit(AppConfig.DEFAULT_DOMAIN)
        self.domain_input.setText(AppConfig.DEFAULT_DOMAIN)
        
        # Interval input
        interval_label = QLabel("Ping Interval (seconds):")
        interval_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        interval_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        
        self.interval_input = ModernDoubleSpinBox()
        self.interval_input.setRange(0.1, 60.0)
        self.interval_input.setValue(AppConfig.DEFAULT_INTERVAL)
        self.interval_input.setDecimals(1)
        self.interval_input.setSingleStep(0.1)
        self.interval_input.setSuffix(" sec")
        self.interval_input.setButtonSymbols(ModernDoubleSpinBox.ButtonSymbols.NoButtons)
        
        # Duration input
        duration_label = QLabel("Test Duration (seconds):")
        duration_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        duration_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        
        self.duration_input = ModernSpinBox()
        self.duration_input.setRange(10, 3600)
        self.duration_input.setValue(AppConfig.DEFAULT_DURATION)
        self.duration_input.setSuffix(" sec")
        self.duration_input.setButtonSymbols(ModernSpinBox.ButtonSymbols.NoButtons)
        
        # Graph view controls (now hidden by default)
        self.graph_view_label = QLabel("Graph View:")
        self.graph_view_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.graph_view_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        
        self.graph_view_button = CompactButton("Disabled", "secondary")
        self.graph_view_button.setToolTip("Enable scrolling window mode for the graph")
        self.graph_view_button.clicked.connect(self.on_graph_view_button_clicked)
        
        # Window duration input
        self.window_label = QLabel("Window:")
        self.window_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.window_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        
        self.follow_window_input = ModernSpinBox()
        self.follow_window_input.setRange(5, 60)
        self.follow_window_input.setValue(AppConfig.DEFAULT_FOLLOW_WINDOW)
        self.follow_window_input.setSuffix(" sec")
        self.follow_window_input.setButtonSymbols(ModernSpinBox.ButtonSymbols.NoButtons)
        self.follow_window_input.setMaximumWidth(100)
        self.follow_window_input.setToolTip("Duration of the scrolling window in seconds")
        self.follow_window_input.valueChanged.connect(self.on_follow_window_changed)
        self.follow_window_input.setEnabled(False)
        
        # Control buttons
        self.start_button = ModernButton("Start Test", primary=True)
        self.start_button.clicked.connect(self.start_test)
        
        self.stop_button = ModernButton("Stop Test")
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setEnabled(False)
        
        # Layout controls - simplified when graph controls are hidden
        controls_layout.addWidget(domain_label, 0, 0)
        controls_layout.addWidget(self.domain_input, 0, 1, 1, 2)  # Span 2 columns
        controls_layout.addWidget(self.graph_view_label, 0, 3)
        controls_layout.addWidget(self.graph_view_button, 0, 4)
        controls_layout.addWidget(interval_label, 0, 5)
        controls_layout.addWidget(self.interval_input, 0, 6)
        
        controls_layout.addWidget(duration_label, 1, 0)
        controls_layout.addWidget(self.duration_input, 1, 1, 1, 2)  # Span 2 columns
        controls_layout.addWidget(self.window_label, 1, 3)
        controls_layout.addWidget(self.follow_window_input, 1, 4)
        controls_layout.addWidget(self.start_button, 1, 5)
        controls_layout.addWidget(self.stop_button, 1, 6)
        
        main_layout.addWidget(controls_frame)
    
    def _create_statistics_cards(self, main_layout):
        """Create statistics display cards"""
        # Basic Statistics cards (always visible)
        self.basic_stats_layout = QHBoxLayout()
        self.current_ping_card = StatCard("Current Ping", "0 ms", Colors.CHART_GREEN)
        self.avg_ping_card = StatCard("Average Ping", "0 ms", Colors.CHART_BLUE)
        self.packet_loss_card = StatCard("Packet Loss", "0%", Colors.CHART_RED)
        self.ping_count_card = StatCard("Ping Count", "0", Colors.CHART_PURPLE)
        
        self.basic_stats_layout.addWidget(self.current_ping_card)
        self.basic_stats_layout.addWidget(self.avg_ping_card)
        self.basic_stats_layout.addWidget(self.packet_loss_card)
        self.basic_stats_layout.addWidget(self.ping_count_card)
        
        main_layout.addLayout(self.basic_stats_layout)
        
        # Advanced Statistics section - initially hidden
        self.advanced_stats_layout = QHBoxLayout()
        self.min_ping_card = StatCard("Min Ping", "0 ms", Colors.CHART_CYAN)
        self.max_ping_card = StatCard("Max Ping", "0 ms", Colors.CHART_ORANGE)
        self.jitter_card = StatCard("Jitter", "0 ms", Colors.CHART_PINK)
        self.status_card = StatCard("Ping Quality", "Ready", Colors.CHART_GRAY)
        
        self.advanced_stats_layout.addWidget(self.min_ping_card)
        self.advanced_stats_layout.addWidget(self.max_ping_card)
        self.advanced_stats_layout.addWidget(self.jitter_card)
        self.advanced_stats_layout.addWidget(self.status_card)
        
        main_layout.addLayout(self.advanced_stats_layout)
    
    def _create_graph_container(self, main_layout):
        """Create the graph container"""
        graph_container = QWidget()
        graph_layout = QVBoxLayout(graph_container)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # Graph with hover functionality
        self.graph_widget = HoverPlotWidget()
        self.graph_widget.setMinimumHeight(400)
        
        graph_layout.addWidget(self.graph_widget)
        main_layout.addWidget(graph_container)
    
    def _setup_graph(self):
        """Setup the graph widget and plot line"""
        # Create plot line with larger symbols for better hovering
        self.plot_line = self.graph_widget.create_plot_line()
        
        # Connect view range changed signal to detect manual zoom/pan
        self.graph_widget.sigRangeChanged.connect(self.on_range_changed)
    
        # Connect reset view button signal
        self.graph_widget.reset_view_requested.connect(self.reset_view)

    def _apply_theme(self):
        """Apply the dark theme to the main window"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {Colors.PRIMARY_BG};
            }}
            QLabel {{
                color: {Colors.PRIMARY_TEXT};
            }}
        """)
    
    # Settings Management
    def show_settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self, self.show_advanced_stats, self.show_graph_controls)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.show_advanced_stats = settings['show_advanced_stats']
            self.show_graph_controls = settings['show_graph_controls']
            self._update_ui_visibility()
    
    def _update_ui_visibility(self):
        """Update UI element visibility based on settings"""
        # Show/hide advanced statistics
        for i in range(self.advanced_stats_layout.count()):
            item = self.advanced_stats_layout.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(self.show_advanced_stats)
        
        # Show/hide graph controls
        self.graph_view_label.setVisible(self.show_graph_controls)
        self.graph_view_button.setVisible(self.show_graph_controls)
        self.window_label.setVisible(self.show_graph_controls)
        self.follow_window_input.setVisible(self.show_graph_controls)
    
    # Graph View Management
    def on_graph_view_button_clicked(self):
        """Handle graph view button clicks"""
        # Toggle the follow mode state
        self.follow_mode_enabled = not self.follow_mode_enabled
        
        # Update button text and style
        if self.follow_mode_enabled:
            self.graph_view_button.setText("Enabled")
            self.graph_view_button.style_type = "success"
        else:
            self.graph_view_button.setText("Disabled")
            self.graph_view_button.style_type = "secondary"
        
        # Refresh button styling
        self.graph_view_button._setup_style()
        
        # Update follow window input state
        self.follow_window_input.setEnabled(self.follow_mode_enabled)
        
        if self.follow_mode_enabled:
            # Disable auto-range when follow mode is enabled
            self.auto_range_enabled = False
            self.follow_window_seconds = self.follow_window_input.value()
        else:
            # Re-enable auto-range when follow mode is disabled
            self.auto_range_enabled = True
            
        # Update graph view immediately if we have data
        if self.data_manager.has_data():
            self.update_graph_view()
    
    def on_follow_window_changed(self, value):
        """Handle follow window duration changes"""
        self.follow_window_seconds = value
        if self.follow_mode_enabled:
            # Update graph view immediately if we have data
            if self.data_manager.has_data():
                self.update_graph_view()
    
    def on_range_changed(self):
        """Called when the graph view range changes (zoom/pan)"""
        if not self.follow_mode_enabled and self.is_running and self.data_manager.has_data():
            # Check if we're still in auto-range mode (only when not in follow mode)
            view_box = self.graph_widget.getViewBox()
            current_range = view_box.viewRange()
            
            # Calculate what the auto range should be
            timestamps, _ = self.data_manager.get_data_arrays()
            if len(timestamps) > 1:
                x_range = [min(timestamps), max(timestamps)]
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
            else:
                # We're still in auto range
                self.auto_range_enabled = True
    
    def reset_view(self):
        """Reset the graph view to auto-range mode"""
        self.auto_range_enabled = True
        self.follow_mode_enabled = False
        
        # Update UI
        if self.show_graph_controls:
            self.graph_view_button.setText("Disabled")
            self.graph_view_button.style_type = "secondary"
            self.graph_view_button._setup_style()
            self.follow_window_input.setEnabled(False)
        
        # Reset graph view
        if self.data_manager.has_data():
            self.graph_widget.enableAutoRange()
        else:
            self.graph_widget.setRange(xRange=[-1, 1], yRange=[0, 100])
    
    def update_graph_view(self):
        """Update the graph view based on current mode"""
        timestamps, ping_times = self.data_manager.get_data_arrays()
        if not timestamps:
            return
            
        if self.follow_mode_enabled:
            # Follow mode: show only the last N seconds
            current_time = max(timestamps)
            window_start = current_time - self.follow_window_seconds
            
            # Find data points within the window
            visible_times = []
            visible_pings = []
            
            for i, timestamp in enumerate(timestamps):
                if timestamp >= window_start:
                    visible_times.append(timestamp)
                    visible_pings.append(ping_times[i])
            
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
    
    # Network Testing
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
    
    # CSV Export
    def export_to_csv(self):
        """Export ping data to CSV file"""
        domain = self.domain_input.text().strip()
        self.data_manager.export_to_csv(self, domain)
    
    # Test Control
    def start_test(self):
        """Start the ping test"""
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
        
        # Update UI state with animations
        self.is_running = True
        self.data_manager.set_start_time(datetime.now())
        
        # Update status
        if self.show_advanced_stats:
            self.status_card.update_value("Ready")
            self.status_card.value_label.setStyleSheet(f"color: {Colors.CHART_GRAY};")
        
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
        """Stop the ping test"""
        self.is_running = False
        self.ping_worker.stop_pinging()
        self.test_timer.stop()
        
        # Update status
        if self.show_advanced_stats:
            self.status_card.update_value("Ready")
            self.status_card.value_label.setStyleSheet(f"color: {Colors.CHART_GRAY};")
        
        # Remove danger mode
        self.stop_button.set_danger_mode(False)
        
        # Update UI state with animations
        self.start_button.animate_state_change(True)
        self.stop_button.animate_state_change(False)
    
    def clear_data(self):
        """Clear all data and reset UI"""
        self.data_manager.clear_data()
        
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
            self.status_card.value_label.setStyleSheet(f"color: {Colors.CHART_GRAY};")
        
        # Disable export button when no data
        self.export_csv_button.setEnabled(False)
    
    # Ping Result Handlers
    def on_ping_result(self, ping_time):
        """Handle successful ping result"""
        if not self.is_running:
            return
            
        current_time = (datetime.now() - self.data_manager.start_time).total_seconds()
        
        # Add data to manager
        self.data_manager.add_ping_result(ping_time, current_time)
        
        # Update graph
        timestamps, ping_times = self.data_manager.get_data_arrays()
        self.plot_line.setData(timestamps, ping_times)
        
        # Update hover data
        self.graph_widget.update_data(timestamps, ping_times, self.data_manager.start_time)
        
        # Update graph view based on current mode
        self.update_graph_view()
        
        # Update statistics
        self._update_statistics_display(ping_time)
    
    def on_ping_failed(self):
        """Handle ping failure"""
        if not self.is_running:
            return
            
        self.data_manager.add_ping_failure()
        
        # Update packet loss display
        basic_stats = self.data_manager.get_basic_statistics()
        self.packet_loss_card.update_value(f"{basic_stats['packet_loss']:.1f}%")
        
        # Update status to show connection issues (only if advanced stats enabled)
        if self.show_advanced_stats:
            self.status_card.update_value("Connection Issue")
            self.status_card.value_label.setStyleSheet(f"color: {Colors.DANGER};")
    
    def _update_statistics_display(self, current_ping):
        """Update all statistics displays"""
        # Get statistics from data manager
        basic_stats = self.data_manager.get_basic_statistics()
        
        # Update basic statistics (always visible)
        self.current_ping_card.update_value(f"{current_ping:.1f} ms")
        self.avg_ping_card.update_value(f"{basic_stats['avg_ping']:.1f} ms")
        self.packet_loss_card.update_value(f"{basic_stats['packet_loss']:.1f}%")
        self.ping_count_card.update_value(str(basic_stats['ping_count']))
        
        # Update advanced statistics (only if enabled)
        if self.show_advanced_stats:
            advanced_stats = self.data_manager.get_advanced_statistics()
            
            self.min_ping_card.update_value(f"{advanced_stats['min_ping']:.1f} ms")
            self.max_ping_card.update_value(f"{advanced_stats['max_ping']:.1f} ms")
            self.jitter_card.update_value(f"{advanced_stats['jitter']:.1f} ms")
            
            # Update status with color coding based on ping quality
            status_text, status_color = self.data_manager.get_ping_quality_status(current_ping)
            self.status_card.update_value(status_text)
            self.status_card.value_label.setStyleSheet(f"color: {status_color};")


def setup_application():
    """Setup the PyQt application with proper configuration"""
    # Windows-specific setup for taskbar icon
    if platform.system() == "Windows":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(AppConfig.APP_ID)
        except Exception:
            # Silently fail if there are issues (e.g., on older Windows versions)
            pass
    
    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.APP_NAME)
    app.setApplicationVersion(AppConfig.APP_VERSION)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set window icon if available
    try:
        app.setWindowIcon(QIcon('assets/icons/ping-poller.ico'))
    except Exception:
        pass  # Icon file not found, continue without it
    
    return app


def main():
    """Main application entry point"""
    app = setup_application()
    
    window = PingPoller()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()