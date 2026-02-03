from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StatusIndicator(QFrame):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Status Label
        self.status_label = QLabel("STATUS: IDLE")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #ecf0f1; border: 2px solid #bdc3c7; padding: 10px; border-radius: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # Calibration Status Sub-label
        self.calib_status = QLabel("Calibration: PENDING ❌")
        self.calib_status.setFont(QFont("Arial", 10))
        self.calib_status.setStyleSheet("color: #e74c3c; margin-top: 5px;") # Red
        self.calib_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.calib_status)

    def update_status(self, text: str, color: str):
        """Update the main status text"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; border: 2px solid {color}; padding: 10px; border-radius: 5px;")
    
    def set_calibration_status(self, is_calibrated: bool):
        if is_calibrated:
            self.calib_status.setText("Calibration: DONE ✅")
            self.calib_status.setStyleSheet("color: #2ecc71; margin-top: 5px;") # Green
        else:
            self.calib_status.setText("Calibration: PENDING ❌")
            self.calib_status.setStyleSheet("color: #e74c3c; margin-top: 5px;") # Red

    def reset(self):
        self.update_status("STATUS: IDLE", "#bdc3c7")
        self.set_calibration_status(False)
