# ui_widgets.py
"""
Custom UI widgets for the Ping Poller application.
"""

from PyQt6.QtWidgets import (QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox, 
                             QCheckBox, QFrame, QVBoxLayout, QLabel, QDialog,
                             QDialogButtonBox, QGroupBox, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from constants import Colors


class ModernButton(QPushButton):
    """Modern styled button with animation support and danger mode"""
    
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
        """Setup button styling based on type"""
        if self.primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.PRIMARY_BLUE}, stop: 1 {Colors.PRIMARY_BLUE_PRESSED});
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.PRIMARY_BLUE_HOVER}, stop: 1 {Colors.PRIMARY_BLUE});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.PRIMARY_BLUE_PRESSED}, stop: 1 {Colors.PRIMARY_BLUE_DARK});
                }}
                QPushButton:disabled {{
                    background: {Colors.DISABLED_BG};
                    color: {Colors.DISABLED_TEXT};
                }}
            """)
        elif self.is_danger_mode:
            # Red styling for danger state
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.DANGER}, stop: 1 {Colors.DANGER_PRESSED});
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.DANGER_HOVER}, stop: 1 {Colors.DANGER});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.DANGER_PRESSED}, stop: 1 {Colors.DANGER_DARK});
                }}
                QPushButton:disabled {{
                    background: {Colors.DISABLED_BG};
                    color: {Colors.DISABLED_TEXT};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Colors.TERTIARY_BG};
                    color: {Colors.PRIMARY_TEXT};
                    border: 1px solid {Colors.SECONDARY_BORDER};
                    border-radius: 8px;
                    font-weight: 500;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: {Colors.HOVER_BG};
                    border-color: {Colors.TERTIARY_BORDER};
                }}
                QPushButton:pressed {{
                    background: {Colors.PRESSED_BG};
                }}
                QPushButton:disabled {{
                    background: {Colors.SECONDARY_BG};
                    color: {Colors.MUTED_TEXT};
                    border-color: {Colors.DISABLED_BG};
                }}
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
    """Smaller button for header area with different color schemes"""
    
    def __init__(self, text, style="secondary"):
        super().__init__(text)
        self.style_type = style
        self.setMinimumHeight(32)
        self.setMaximumHeight(32)
        self.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self._setup_style()
        
    def _setup_style(self):
        """Setup styling based on button type"""
        if self.style_type == "success":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.SUCCESS}, stop: 1 {Colors.SUCCESS_PRESSED});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.SUCCESS_HOVER}, stop: 1 {Colors.SUCCESS});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.SUCCESS_PRESSED}, stop: 1 {Colors.SUCCESS_DARK});
                }}
                QPushButton:disabled {{
                    background: {Colors.DISABLED_BG};
                    color: {Colors.DISABLED_TEXT};
                }}
            """)
        elif self.style_type == "info":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.INFO}, stop: 1 {Colors.INFO_PRESSED});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.INFO_HOVER}, stop: 1 {Colors.INFO});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.INFO_PRESSED}, stop: 1 {Colors.INFO_DARK});
                }}
                QPushButton:disabled {{
                    background: {Colors.DISABLED_BG};
                    color: {Colors.DISABLED_TEXT};
                }}
            """)
        elif self.style_type == "settings":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.PURPLE}, stop: 1 {Colors.PURPLE_PRESSED});
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.PURPLE_HOVER}, stop: 1 {Colors.PURPLE});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                stop: 0 {Colors.PURPLE_PRESSED}, stop: 1 {Colors.PURPLE_DARK});
                }}
                QPushButton:disabled {{
                    background: {Colors.DISABLED_BG};
                    color: {Colors.DISABLED_TEXT};
                }}
            """)
        else:  # secondary
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Colors.TERTIARY_BG};
                    color: {Colors.PRIMARY_TEXT};
                    border: 1px solid {Colors.SECONDARY_BORDER};
                    border-radius: 6px;
                    font-weight: 500;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background: {Colors.HOVER_BG};
                    border-color: {Colors.TERTIARY_BORDER};
                }}
                QPushButton:pressed {{
                    background: {Colors.PRESSED_BG};
                }}
                QPushButton:disabled {{
                    background: {Colors.SECONDARY_BG};
                    color: {Colors.MUTED_TEXT};
                    border-color: {Colors.DISABLED_BG};
                }}
            """)


class ModernLineEdit(QLineEdit):
    """Modern styled line edit input"""
    
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.SECONDARY_BG};
                border: 2px solid {Colors.PRIMARY_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: {Colors.PRIMARY_TEXT};
            }}
            QLineEdit:focus {{
                border-color: {Colors.FOCUS_BORDER};
                outline: none;
            }}
            QLineEdit:hover {{
                border-color: {Colors.SECONDARY_BORDER};
            }}
            QLineEdit::placeholder {{
                color: {Colors.DISABLED_TEXT};
            }}
        """)


class ModernSpinBox(QSpinBox):
    """Modern styled spin box"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QSpinBox {{
                background: {Colors.SECONDARY_BG};
                border: 2px solid {Colors.PRIMARY_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: {Colors.PRIMARY_TEXT};
            }}
            QSpinBox:focus {{
                border-color: {Colors.FOCUS_BORDER};
                outline: none;
            }}
            QSpinBox:hover {{
                border-color: {Colors.SECONDARY_BORDER};
            }}
        """)


class ModernDoubleSpinBox(QDoubleSpinBox):
    """Modern styled double spin box"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background: {Colors.SECONDARY_BG};
                border: 2px solid {Colors.PRIMARY_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
                color: {Colors.PRIMARY_TEXT};
            }}
            QDoubleSpinBox:focus {{
                border-color: {Colors.FOCUS_BORDER};
                outline: none;
            }}
            QDoubleSpinBox:hover {{
                border-color: {Colors.SECONDARY_BORDER};
            }}
        """)


class ModernCheckBox(QCheckBox):
    """Modern styled checkbox"""
    
    def __init__(self, text=""):
        super().__init__(text)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.PRIMARY_TEXT};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {Colors.SECONDARY_BORDER};
                background: {Colors.SECONDARY_BG};
            }}
            QCheckBox::indicator:checked {{
                background: {Colors.PRIMARY_BLUE};
                border-color: {Colors.PRIMARY_BLUE};
            }}
            QCheckBox::indicator:checked:hover {{
                background: {Colors.PRIMARY_BLUE_HOVER};
                border-color: {Colors.PRIMARY_BLUE_HOVER};
            }}
            QCheckBox::indicator:hover {{
                border-color: {Colors.TERTIARY_BORDER};
                background: {Colors.TERTIARY_BG};
            }}
            QCheckBox::indicator:checked::after {{
                content: "✓";
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}
        """)


class StatCard(QFrame):
    """Statistics display card with colored accent"""
    
    def __init__(self, title, value="0 ms", color=Colors.PRIMARY_BLUE):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.SECONDARY_BG};
                border: 1px solid {Colors.PRIMARY_BORDER};
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        title_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
    def update_value(self, value):
        """Update the displayed value"""
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
        self.setStyleSheet(f"""
            QDialog {{
                background: {Colors.PRIMARY_BG};
                color: {Colors.PRIMARY_TEXT};
            }}
            QLabel {{
                color: {Colors.PRIMARY_TEXT};
                font-size: 10pt;
            }}
            QGroupBox {{
                color: {Colors.PRIMARY_TEXT};
                font-weight: bold;
                border: 2px solid {Colors.PRIMARY_BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {Colors.PRIMARY_BLUE};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Display Settings")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Colors.PRIMARY_BLUE}; margin-bottom: 10px;")
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
        advanced_desc.setStyleSheet(f"color: {Colors.SECONDARY_TEXT}; font-size: 9pt; margin-left: 25px;")
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
        graph_desc.setStyleSheet(f"color: {Colors.SECONDARY_TEXT}; font-size: 9pt; margin-left: 25px;")
        graph_layout.addWidget(graph_desc)
        
        layout.addWidget(graph_group)
        
        # Spacer
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.setStyleSheet(f"""
            QDialogButtonBox QPushButton {{
                background: {Colors.TERTIARY_BG};
                color: {Colors.PRIMARY_TEXT};
                border: 1px solid {Colors.SECONDARY_BORDER};
                border-radius: 6px;
                font-weight: 500;
                padding: 8px 16px;
                min-width: 80px;
            }}
            QDialogButtonBox QPushButton:hover {{
                background: {Colors.HOVER_BG};
                border-color: {Colors.TERTIARY_BORDER};
            }}
            QDialogButtonBox QPushButton:pressed {{
                background: {Colors.PRESSED_BG};
            }}
            QDialogButtonBox QPushButton[text="OK"] {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {Colors.PRIMARY_BLUE}, stop: 1 {Colors.PRIMARY_BLUE_PRESSED});
                border: none;
            }}
            QDialogButtonBox QPushButton[text="OK"]:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {Colors.PRIMARY_BLUE_HOVER}, stop: 1 {Colors.PRIMARY_BLUE});
            }}
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