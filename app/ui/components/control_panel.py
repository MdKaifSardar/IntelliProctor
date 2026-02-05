from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar
from PyQt6.QtCore import pyqtSignal, Qt

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
        self.calib_progress.setTextVisible(False)
        self.calib_progress.hide()
        self.layout.addWidget(self.calib_progress)
        
        self.layout.addSpacing(10)
        
        # Calibrate Button
        self.btn_calib = QPushButton("CALIBRATE")
        self.btn_calib.setFixedHeight(40)
        self.btn_calib.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calib.clicked.connect(self._handle_calib_click)
        self.layout.addWidget(self.btn_calib)
        
        self.layout.addSpacing(10)
        
        # Stop Exam Button
        self.btn_stop = QPushButton("END EXAM")
        self.btn_stop.setObjectName("StopButton")
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop_exam_request.emit)
        self.layout.addWidget(self.btn_stop)



    def _handle_calib_click(self):
        # Determine action based on current text/state
        text = self.btn_calib.text()
        if text == "STOP":
            self.stop_calibration_request.emit()
        else:
            # Force UI Reset immediately for feedback
            self.calib_progress.setValue(0)
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
            self.btn_calib.setObjectName("StopButton")
        elif is_calibrated:
            self.btn_calib.setText("RECALIBRATE")
            self.btn_calib.setObjectName("") # Blue
        else:
            self.btn_calib.setText("CALIBRATE")
            self.btn_calib.setObjectName("") # Blue

        # Refresh Style
        self.btn_calib.style().unpolish(self.btn_calib)
        self.btn_calib.style().polish(self.btn_calib)

    def update_progress(self, value: int):
        self.calib_progress.setValue(value)

    def reset(self):
        self.update_state(is_calibrating=False, is_calibrated=False)
        self.calib_progress.setValue(0)
