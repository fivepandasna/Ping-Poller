# constants.py
"""
Application constants including colors and configuration values.
"""

class Colors:
    """Color constants for the dark theme UI"""
    
    # Background colors
    PRIMARY_BG = "#1E1E1E"
    SECONDARY_BG = "#2A2A2A"
    TERTIARY_BG = "#3A3A3A"
    HOVER_BG = "#464646"
    PRESSED_BG = "#2E2E2E"
    DISABLED_BG = "#444444"
    
    # Text colors
    PRIMARY_TEXT = "#E0E0E0"
    SECONDARY_TEXT = "#AAAAAA"
    DISABLED_TEXT = "#888888"
    MUTED_TEXT = "#666666"
    
    # Border colors
    PRIMARY_BORDER = "#444444"
    SECONDARY_BORDER = "#555555"
    TERTIARY_BORDER = "#666666"
    FOCUS_BORDER = "#4A90E2"
    
    # Brand colors
    PRIMARY_BLUE = "#4A90E2"
    PRIMARY_BLUE_HOVER = "#5BA0F2"
    PRIMARY_BLUE_PRESSED = "#357ABD"
    PRIMARY_BLUE_DARK = "#2E6BA8"
    
    # Status colors
    SUCCESS = "#28A745"
    SUCCESS_HOVER = "#34CE57"
    SUCCESS_PRESSED = "#1E7E34"
    SUCCESS_DARK = "#155724"
    
    INFO = "#17A2B8"
    INFO_HOVER = "#20C0DB"
    INFO_PRESSED = "#138496"
    INFO_DARK = "#0C6674"
    
    WARNING = "#FFC107"
    WARNING_ORANGE = "#FD7E14"
    
    DANGER = "#DC3545"
    DANGER_HOVER = "#EC7063"
    DANGER_PRESSED = "#C0392B"
    DANGER_DARK = "#A93226"
    
    # Special colors
    PURPLE = "#6F42C1"
    PURPLE_HOVER = "#8A5CF5"
    PURPLE_PRESSED = "#5A31A5"
    PURPLE_DARK = "#4C2A91"
    
    PINK = "#E83E8C"
    GRAY = "#6C757D"
    
    # Chart colors
    CHART_BLUE = PRIMARY_BLUE
    CHART_GREEN = SUCCESS
    CHART_RED = DANGER
    CHART_PURPLE = PURPLE
    CHART_CYAN = INFO
    CHART_ORANGE = WARNING_ORANGE
    CHART_PINK = PINK
    CHART_GRAY = GRAY


class AppConfig:
    """Application configuration constants"""
    
    # Application info
    APP_NAME = "Ping Poller"
    APP_VERSION = "1.0.0"
    APP_ID = "PingPoller.1.0.0"
    
    # Window settings
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800
    MIN_WINDOW_POS_X = 100
    MIN_WINDOW_POS_Y = 100
    
    # Data limits
    MAX_PING_HISTORY = 1000
    MAX_RECENT_PINGS = 100
    
    # Default values
    DEFAULT_DOMAIN = "google.com"
    DEFAULT_INTERVAL = 1.0
    DEFAULT_DURATION = 60
    DEFAULT_FOLLOW_WINDOW = 10
    
    # Network test hosts
    NETWORK_TEST_HOSTS = ["8.8.8.8", "1.1.1.1", "google.com"]
    
    # Timeouts (seconds)
    PING_TIMEOUT = 5
    NETWORK_TEST_TIMEOUT = 3