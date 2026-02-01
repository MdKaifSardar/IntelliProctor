from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class HomePage(QWidget):
    start_exam_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #ecf0f1;")
        
        # Title
        title = QLabel("Intelligent Proctoring System")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Please ensure you are in a well-lit room.")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 40px;")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Start Button
        btn_start = QPushButton("START EXAM")
        btn_start.setFixedSize(200, 60)
        btn_start.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; 
                color: white; 
                border-radius: 30px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_start.clicked.connect(self.start_exam_signal.emit)
        layout.addWidget(btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
