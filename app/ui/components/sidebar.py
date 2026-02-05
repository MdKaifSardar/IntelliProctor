from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import Sub-Components
from .status_indicator import StatusIndicator
from .telemetry_panel import TelemetryPanel
from .event_log import EventLog
from .control_panel import ControlPanel

class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)
        
        self.layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Proctor Controls")
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)
        
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
        self.layout.addWidget(self.log) # Takes remaining vertical space naturally? No, need stretch.
        
        self.layout.addSpacing(10)
        
        # 4. Control Panel (Buttons + Progress)
        self.controls = ControlPanel()
        self.layout.addWidget(self.controls)
        
        self.layout.addSpacing(20)

    def reset(self):
        """Reset all child components"""
        self.status_indicator.reset()
        self.telemetry.reset()
        self.log.reset()
        self.controls.reset()
