from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtGui import QImage
from app.core.schemas import RiskEvent

# Import Modular Components
from app.ui.components.video_feed import VideoFeed
from app.ui.components.sidebar import Sidebar

class ProctorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main Layout: Horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Video Feed (Left) - Takes 75%
        self.video_feed = VideoFeed()
        layout.addWidget(self.video_feed, stretch=3)
        
        # 2. Sidebar (Right) - Fixed Width
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)
        
        # Expose Signals for Controller
        # We proxy the signals from the deep components up to this surface
        self.recalibrate_request = self.sidebar.controls.recalibrate_request
        self.stop_request = self.sidebar.controls.stop_exam_request
        self.stop_calibration_request = self.sidebar.controls.stop_calibration_request

    def update_frame(self, qt_image: QImage):
        self.video_feed.update_frame(qt_image)

    def log_message(self, message: str, color: str = "white"):
        self.sidebar.log.log_message(message, color)

    def log_risk_event(self, event: RiskEvent):
        self.sidebar.log.log_risk_event(event)

    def update_status(self, text: str, color: str):
        self.sidebar.status_indicator.update_status(text, color)

    def update_stats(self, stats: dict):
        # 1. Update Telemetry
        self.sidebar.telemetry.update_stats(stats)
        
        # 2. Update Calibration Status Logic
        is_calibrated = False
        is_calibrating = stats.get("is_calibrating", False)
        
        # Logic to determine if we show "Done" or "Pending"
        # If we have valid pose data and are not calibrating, we are calibrated.
        if not is_calibrating and "yaw" in stats:
            is_calibrated = True
            
        self.sidebar.status_indicator.set_calibration_status(is_calibrated)
        
        # 3. Update Controls (Progress & Button State)
        self.sidebar.controls.update_state(is_calibrating, is_calibrated)
        
        if "calibration_progress" in stats:
             self.sidebar.controls.update_progress(int(stats["calibration_progress"] * 100))
             
    def reset_ui(self):
        """Resets all UI elements"""
        self.video_feed.reset()
        self.sidebar.reset()
