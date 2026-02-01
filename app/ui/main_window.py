from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import pyqtSlot
from app.ui.home_page import HomePage
from app.ui.proctor_page import ProctorPage
from app.ui.worker import ProctorWorker
from app.infrastructure.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelligent Proctoring System")
        self.resize(1024, 768)
        
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
        self.proctor_page.recalibrate_request.connect(self.handle_recalibrate)

    @pyqtSlot()
    def start_exam(self):
        """Switch to Proctor Page and Start CV Worker"""
        self.stack.setCurrentWidget(self.proctor_page)
        
        # Initialize Worker
        if self.worker is None:
            self.worker = ProctorWorker()
            
            # Connect Worker -> UI
            self.worker.image_signal.connect(self.proctor_page.update_frame)
            self.worker.status_signal.connect(self.proctor_page.update_status)
            self.worker.stats_signal.connect(self.proctor_page.update_stats)
            
            self.worker.start()

    @pyqtSlot()
    def stop_exam(self):
        """Stop Worker and Switch to Home"""
        if self.worker:
            self.worker.stop()
            self.worker = None
            
        self.stack.setCurrentWidget(self.home_page)

    @pyqtSlot()
    def handle_recalibrate(self):
        """
        Handle the single button click.
        Context-aware:
        - If button says "STOP", call stop_calibration.
        - Else, call recalibrate (Start).
        """
        # We need to know the current state.
        # We can check the button text directly from the page if we want,
        # or rely on a flag. Checking text is simple/robust for this UI-driven logic.
        # Note: We need to access the pages correctly.
        # The proctor_page is at index 1 (stacked widget).
        
        # proctor_page = self.pages.widget(1) # Assuming ProctorPage is index 1
        # Better: self.proctor_page if we stored it as attribute (we did in init_ui)
        
        btn_text = self.proctor_page.btn_calib.text()
        
        if btn_text == "STOP":
            logger.info("User requested to STOP calibration.")
            if self.worker:
                self.worker.stop_calibration()
        else:
            logger.info("User requested to START/RE-CALIBRATE.")
            if self.worker:
                self.worker.recalibrate()
