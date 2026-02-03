from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont

class TelemetryPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #34495e; border-radius: 5px; padding: 5px;")
        self.layout = QVBoxLayout(self)
        
        t_title = QLabel("Real-time Stats")
        t_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        t_title.setStyleSheet("color: #ecf0f1; border: none;")
        self.layout.addWidget(t_title)
        
        self.pose_label = QLabel("Pose: -")
        self.pose_label.setStyleSheet("border: none; font-size: 12px; color: #ecf0f1;")
        self.layout.addWidget(self.pose_label)
        
        self.audio_label = QLabel("Audio: -")
        self.audio_label.setStyleSheet("border: none; font-size: 12px; color: #ecf0f1;")
        self.layout.addWidget(self.audio_label)
        
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #e74c3c; border: none; font-weight: bold; font-size: 12px;")
        self.warning_label.setWordWrap(True)
        self.layout.addWidget(self.warning_label)
        
    def update_stats(self, stats: dict):
        if "yaw" in stats:
            self.pose_label.setText(f"Pose: Y:{stats['yaw']} P:{stats['pitch']}")
        
        if "audio_db" in stats:
            self.audio_label.setText(f"Audio: {stats['audio_db']}")
            
        if "warning" in stats:
            self.warning_label.setText(f"⚠ {stats['warning']}")
        else:
            self.warning_label.setText("")

    def reset(self):
        self.pose_label.setText("Pose: -")
        self.audio_label.setText("Audio: -")
        self.warning_label.setText("")
