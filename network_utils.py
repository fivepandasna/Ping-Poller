# network_utils.py
"""
Network utilities for ping testing and connectivity checks.
"""

import threading
import time
import subprocess
import platform
import re
from PyQt6.QtCore import QObject, pyqtSignal
from constants import AppConfig


class NetworkTester(QObject):
    """Test network connectivity to multiple reliable hosts"""
    
    test_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self):
        super().__init__()
        
    def test_connection(self):
        """Test network connectivity to multiple reliable hosts"""
        thread = threading.Thread(target=self._test_connection_thread, daemon=True)
        thread.start()
        
    def _test_connection_thread(self):
        """Test connectivity in a separate thread"""
        for host in AppConfig.NETWORK_TEST_HOSTS:
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
                timeout=AppConfig.NETWORK_TEST_TIMEOUT,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            return result.returncode == 0
        except Exception:
            return False


class PingWorker(QObject):
    """Worker class for continuous ping operations"""
    
    ping_result = pyqtSignal(float)
    ping_failed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.domain = ""
        self.interval = 1.0
        
    def start_pinging(self, domain, interval):
        """Start continuous pinging"""
        self.domain = domain
        self.interval = interval
        self.running = True
        thread = threading.Thread(target=self._ping_loop, daemon=True)
        thread.start()
        
    def stop_pinging(self):
        """Stop continuous pinging"""
        self.running = False
        
    def _ping_loop(self):
        """Main ping loop running in separate thread"""
        while self.running:
            ping_time = self._ping_host(self.domain)
            if ping_time is not None:
                self.ping_result.emit(ping_time)
            else:
                self.ping_failed.emit()
            time.sleep(self.interval)
            
    def _ping_host(self, host):
        """Ping a single host and return response time in milliseconds"""
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
                timeout=AppConfig.PING_TIMEOUT,
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