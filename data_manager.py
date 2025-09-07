# data_manager.py
"""
Data management for ping statistics and CSV export functionality.
"""

import csv
from datetime import datetime, timedelta
from collections import deque
import numpy as np
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from constants import AppConfig


class PingDataManager:
    """Manages ping data storage, statistics, and export functionality"""
    
    def __init__(self):
        # Data storage
        self.ping_times = deque(maxlen=AppConfig.MAX_PING_HISTORY)
        self.timestamps = deque(maxlen=AppConfig.MAX_PING_HISTORY)
        self.start_time = None
        
        # Statistics
        self.ping_count = 0
        self.failed_count = 0
        self.total_ping_time = 0
        self.min_ping = float('inf')
        self.max_ping = 0
        self.recent_pings = deque(maxlen=AppConfig.MAX_RECENT_PINGS)
    
    def clear_data(self):
        """Reset all data and statistics"""
        self.ping_times.clear()
        self.timestamps.clear()
        self.ping_count = 0
        self.failed_count = 0
        self.total_ping_time = 0
        self.min_ping = float('inf')
        self.max_ping = 0
        self.recent_pings.clear()
        self.start_time = None
    
    def add_ping_result(self, ping_time, current_time):
        """Add a successful ping result"""
        self.ping_times.append(ping_time)
        self.timestamps.append(current_time)
        self.ping_count += 1
        self.total_ping_time += ping_time
        self.recent_pings.append(ping_time)
        
        # Update min/max
        self.min_ping = min(self.min_ping, ping_time)
        self.max_ping = max(self.max_ping, ping_time)
    
    def add_ping_failure(self):
        """Record a ping failure"""
        self.failed_count += 1
    
    def get_basic_statistics(self):
        """Get basic ping statistics"""
        avg_ping = self.total_ping_time / self.ping_count if self.ping_count > 0 else 0
        total_attempts = self.ping_count + self.failed_count
        packet_loss = (self.failed_count / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'current_ping': self.ping_times[-1] if self.ping_times else 0,
            'avg_ping': avg_ping,
            'packet_loss': packet_loss,
            'ping_count': self.ping_count
        }
    
    def get_advanced_statistics(self):
        """Get advanced ping statistics"""
        # Calculate jitter (standard deviation of recent pings)
        jitter = 0
        if len(self.recent_pings) >= 2:
            recent_array = np.array(self.recent_pings)
            jitter = np.std(recent_array)
        
        min_ping_value = self.min_ping if self.min_ping != float('inf') else 0
        
        return {
            'min_ping': min_ping_value,
            'max_ping': self.max_ping,
            'jitter': jitter
        }
    
    def get_ping_quality_status(self, current_ping):
        """Get connection quality status based on current ping"""
        if current_ping < 50:
            return "Excellent", "#28A745"  # Green
        elif current_ping < 100:
            return "Good", "#FFC107"       # Yellow
        elif current_ping < 200:
            return "Fair", "#FD7E14"       # Orange
        else:
            return "Poor", "#DC3545"       # Red
    
    def has_data(self):
        """Check if we have any ping data"""
        return len(self.ping_times) > 0
    
    def get_data_arrays(self):
        """Get data as lists for plotting"""
        return list(self.timestamps), list(self.ping_times)
    
    def export_to_csv(self, parent_widget, domain):
        """Export ping data to CSV file"""
        if not self.has_data():
            QMessageBox.information(parent_widget, "Export CSV", 
                                  "No ping data to export. Run a test first.")
            return
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Export Ping Data to CSV",
            f"ping_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            self._write_csv_file(file_path, domain)
            QMessageBox.information(parent_widget, "Export Complete", 
                                  f"Ping data exported successfully to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(parent_widget, "Export Error", 
                               f"Failed to export data:\n{str(e)}")
    
    def _write_csv_file(self, file_path, domain):
        """Write the actual CSV file"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Timestamp', 'Elapsed_Time_Seconds', 'Ping_Time_MS', 
                'Target_Host', 'Test_Start_Time'
            ])
            
            # Write data
            target_host = domain.strip() if domain.strip() else "Unknown"
            start_time_str = self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else "Unknown"
            
            for elapsed_time, ping_time in zip(self.timestamps, self.ping_times):
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
            self._write_summary_statistics(writer)
    
    def _write_summary_statistics(self, writer):
        """Write summary statistics to CSV"""
        writer.writerow([])  # Empty row
        writer.writerow(['=== SUMMARY STATISTICS ==='])
        writer.writerow(['Metric', 'Value'])
        
        basic_stats = self.get_basic_statistics()
        advanced_stats = self.get_advanced_statistics()
        
        writer.writerow(['Total Pings', str(self.ping_count)])
        writer.writerow(['Failed Pings', str(self.failed_count)])
        writer.writerow(['Packet Loss %', f"{basic_stats['packet_loss']:.1f}%"])
        writer.writerow(['Average Ping (ms)', f"{basic_stats['avg_ping']:.1f}"])
        writer.writerow(['Minimum Ping (ms)', f"{advanced_stats['min_ping']:.1f}"])
        writer.writerow(['Maximum Ping (ms)', f"{advanced_stats['max_ping']:.1f}"])
        writer.writerow(['Jitter (ms)', f"{advanced_stats['jitter']:.1f}"])
        writer.writerow(['Test Duration (seconds)', f"{max(self.timestamps) if self.timestamps else 0:.1f}"])
    
    def set_start_time(self, start_time):
        """Set the test start time"""
        self.start_time = start_time