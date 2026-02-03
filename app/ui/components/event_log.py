from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QDateTime
from app.core.schemas import RiskEvent

class EventLog(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        log_label = QLabel("Event Log")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        log_label.setStyleSheet("color: white;")
        self.layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #34495e; color: #ecf0f1; border: none; font-size: 11px;")
        self.layout.addWidget(self.log_text)

    def log_message(self, message: str, color: str = "white"):
        """Log a generic message"""
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        html = f"<span style='color: grey'>[{timestamp}]</span> <span style='color: {color}'>{message}</span>"
        self.log_text.append(html)

    def log_risk_event(self, event: RiskEvent):
        """Log a rich risk event"""
        color = "white"
        if event.risk_level.value == "HIGH": color = "#ff5555"
        elif event.risk_level.value == "MEDIUM": color = "#f1c40f"
        elif event.risk_level.value == "LOW": color = "#bdc3c7"
        
        reasons_str = ", ".join(event.reasons)
        self.log_message(f"<b style='color: {color}'>{event.risk_level.value}</b>: {reasons_str}", "white")

    def reset(self):
        self.log_text.clear()
