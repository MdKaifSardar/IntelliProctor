from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize

# Import Sub-Components
from .status_indicator import StatusIndicator
from .telemetry_panel import TelemetryPanel
from .event_log import EventLog
from .control_panel import ControlPanel

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        
        # Dimensions
        self.EXPANDED_WIDTH = 250
        self.COLLAPSED_WIDTH = 0
        
        self.setFixedWidth(self.EXPANDED_WIDTH)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.max_animation = QPropertyAnimation(self, b"maximumWidth")
        self.max_animation.setDuration(300)
        self.max_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # Add padding
        
        # Title
        self.title = QLabel("Proctor Controls")
        self.title.setObjectName("SidebarTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        self.layout.addSpacing(10)
        
        # 1. Status Indicator
        self.status_indicator = StatusIndicator()
        self.layout.addWidget(self.status_indicator)
        
        self.layout.addSpacing(10)
        
        # 2. Telemetry Panel
        self.telemetry = TelemetryPanel()
        self.layout.addWidget(self.telemetry)
        
        self.layout.addSpacing(10)
        
        # 3. Event Log
        self.log = EventLog()
        self.layout.addWidget(self.log) 
        
        self.layout.addSpacing(10)
        
        # 4. Control Panel (Buttons + Progress)
        self.controls = ControlPanel()
        self.layout.addWidget(self.controls)
        
        self.layout.addSpacing(20)

    def toggle(self):
        width = self.width()
        
        if width == self.EXPANDED_WIDTH:
            new_width = self.COLLAPSED_WIDTH
            self.title.hide() 
            self.controls.hide()
            self.status_indicator.hide()
            self.telemetry.hide()
            self.log.hide()
        else:
            new_width = self.EXPANDED_WIDTH
            self.title.show()
            self.controls.show()
            self.status_indicator.show()
            self.telemetry.show()
            self.log.show()

        self.animation.setStartValue(width)
        self.animation.setEndValue(new_width)
        self.animation.start()
        
        self.max_animation.setStartValue(width)
        self.max_animation.setEndValue(new_width)
        self.max_animation.start()

    def reset(self):
        """Reset all child components"""
        self.status_indicator.reset()
        self.telemetry.reset()
        self.log.reset()
        self.controls.reset()
