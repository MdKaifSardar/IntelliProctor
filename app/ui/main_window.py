from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import pyqtSlot
from app.ui.home_page import HomePage
from app.ui.proctor_page import ProctorPage
from app.ui.worker import ProctorWorker
from app.infrastructure.logger import logger

from app.ui.styles import GLOBAL_STYLES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelligent Proctoring System")
        self.resize(1024, 768)
        self.setStyleSheet(GLOBAL_STYLES)
        
        # Central Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Pages
        self.home_page = HomePage()
        self.proctor_page = ProctorPage()
        
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.proctor_page)
        
        # Worker (Created on demand)
        self.worker = None
        
        # Signals
        self.home_page.start_exam_signal.connect(self.start_exam)
        self.proctor_page.stop_request.connect(self.stop_exam)
        self.proctor_page.recalibrate_request.connect(self.start_calibration)
        self.proctor_page.stop_calibration_request.connect(self.stop_calibration)

    @pyqtSlot()
    def start_exam(self):
        """Switch to Proctor Page and Start CV Worker"""
        self.proctor_page.reset_ui() # Ensure fresh UI
        self.stack.setCurrentWidget(self.proctor_page)
        
        # Initialize Worker
        if self.worker is None:
            self.worker = ProctorWorker()
            
            # Connect Worker -> UI
            self.worker.image_signal.connect(self.proctor_page.update_frame)
            self.worker.status_signal.connect(self.proctor_page.update_status)
            self.worker.stats_signal.connect(self.proctor_page.update_stats)
            self.worker.risk_signal.connect(self.proctor_page.log_risk_event)
            self.worker.log_signal.connect(self.proctor_page.log_message)
            
            self.worker.start()

    @pyqtSlot()
    def stop_exam(self):
        """Stop Worker and Switch to Home"""
        if self.worker:
            self.worker.stop()
            self.worker = None
            
        self.proctor_page.reset_ui()
        self.stack.setCurrentWidget(self.home_page)

    @pyqtSlot()
    def start_calibration(self):
        """User requested to START or REDO calibration"""
        logger.info("User requested to START/RE-CALIBRATE.")
        if self.worker:
            self.worker.recalibrate()

    @pyqtSlot()
    def stop_calibration(self):
        """User requested to STOP calibration"""
        logger.info("User requested to STOP calibration.")
        if self.worker:
            self.worker.stop_calibration()
