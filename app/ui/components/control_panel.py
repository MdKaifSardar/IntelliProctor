from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar
from PyQt6.QtCore import pyqtSignal

class ControlPanel(QWidget):
    # Signals to parent
    recalibrate_request = pyqtSignal()
    stop_calibration_request = pyqtSignal()
    stop_exam_request = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Calibration Progress Bar
        self.calib_progress = QProgressBar()
        self.calib_progress.setRange(0, 100)
        self.calib_progress.setValue(0)
        self.calib_progress.setTextVisible(True)
        self.calib_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
            }
        """)
        self.calib_progress.hide()
        self.layout.addWidget(self.calib_progress)
        
        self.layout.addSpacing(10)
        
        # Calibrate Button
        self.btn_calib = QPushButton("CALIBRATE")
        self.btn_calib.setFixedHeight(50)
        self.btn_calib.setStyleSheet(self._get_btn_style("#e67e22", "#d35400"))
        self.btn_calib.clicked.connect(self._handle_calib_click)
        self.layout.addWidget(self.btn_calib)
        
        self.layout.addSpacing(10)
        
        # Stop Exam Button
        self.btn_stop = QPushButton("END EXAM")
        self.btn_stop.setFixedHeight(50)
        self.btn_stop.setStyleSheet(self._get_btn_style("#e74c3c", "#c0392b"))
        self.btn_stop.clicked.connect(self.stop_exam_request.emit)
        self.layout.addWidget(self.btn_stop)

    def _get_btn_style(self, color, hover_color):
        return f"""
            QPushButton {{
                background-color: {color}; 
                color: white; 
                font-size: 14px; 
                border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """

    def _handle_calib_click(self):
        # Determine action based on current text/state
        text = self.btn_calib.text()
        if text == "STOP":
            self.stop_calibration_request.emit()
        else:
            self.recalibrate_request.emit()

    def update_state(self, is_calibrating: bool, is_calibrated: bool):
        # Progress Bar Logic
        if is_calibrating:
            self.calib_progress.show()
        else:
            self.calib_progress.hide() # Hide when done or idle
            
        # Button Logic
        if is_calibrating:
            self.btn_calib.setText("STOP")
            self.btn_calib.setStyleSheet(self._get_btn_style("#c0392b", "#e74c3c"))
        elif is_calibrated:
            self.btn_calib.setText("RECALIBRATE")
            self.btn_calib.setStyleSheet(self._get_btn_style("#3498db", "#2980b9"))
        else:
            self.btn_calib.setText("CALIBRATE")
            self.btn_calib.setStyleSheet(self._get_btn_style("#e67e22", "#d35400"))

    def update_progress(self, value: int):
        self.calib_progress.setValue(value)

    def reset(self):
        self.update_state(is_calibrating=False, is_calibrated=False)
        self.calib_progress.setValue(0)
