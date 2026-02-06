from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtGui import QImage
from app.core.schemas import RiskEvent

# Import Modular Components
from app.ui.components.video_feed import VideoFeed
from app.ui.components.sidebar import Sidebar
from app.ui.components.top_bar import TopBar

class ProctorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 1. Main Vertical Layout (TopBar + Content)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 2. Top Bar
        self.top_bar = TopBar()
        self.main_layout.addWidget(self.top_bar)
        
        # 3. Content Area (Horizontal: Sidebar + Video)
        # Note: Sidebar on Left or Right? User asked for web app style.
        # Usually sidebar is Left. Let's put it Left.
        
        self.content_area = QWidget()
        self.content_layout = QHBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Sidebar (Left)
        self.sidebar = Sidebar()
        self.content_layout.addWidget(self.sidebar)
        
        # Video Feed (Right)
        self.video_feed = VideoFeed()
        self.content_layout.addWidget(self.video_feed, stretch=1)
        
        self.main_layout.addWidget(self.content_area)
        
        # Connect TopBar Toggle to Sidebar
        self.top_bar.toggle_sidebar_signal.connect(self.sidebar.toggle)
        
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
