from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QImage, QPixmap, QFont
from app.core.schemas import RiskEvent

class ProctorPage(QWidget):
    # Signals for Main Window to handle logic
    recalibrate_request = pyqtSignal()
    stop_request = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main Layout: Horizontal (Video Left, Sidebar Right)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Video Area ---
        self.video_label = QLabel("Waiting for Camera...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        self.video_label.setMinimumSize(640, 480) # 4:3 Aspect Ratio base
        layout.addWidget(self.video_label, stretch=3) # Takes 75% width
        
        # --- Sidebar ---
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Title
        title = QLabel("Proctor Controls")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        
        sidebar_layout.addSpacing(10)
        
        # Status Indicator
        self.status_label = QLabel("STATUS: IDLE")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #ecf0f1; border: 2px solid #bdc3c7; padding: 10px; border-radius: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.status_label)
        
        sidebar_layout.addSpacing(10)

        # Calibration Progress
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
        self.calib_progress.hide() # Hidden by default
        sidebar_layout.addWidget(self.calib_progress)
        
        sidebar_layout.addSpacing(10)
        
        # --- Telemetry Section ---
        telemetry_box = QFrame()
        telemetry_box.setStyleSheet("background-color: #34495e; border-radius: 5px; padding: 5px;")
        t_layout = QVBoxLayout(telemetry_box)
        
        t_title = QLabel("Real-time Stats")
        t_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        t_title.setStyleSheet("color: #ecf0f1; border: none;")
        t_layout.addWidget(t_title)
        
        self.pose_label = QLabel("Pose: -")
        self.pose_label.setStyleSheet("border: none; font-size: 12px;")
        t_layout.addWidget(self.pose_label)
        
        self.audio_label = QLabel("Audio: -")
        self.audio_label.setStyleSheet("border: none; font-size: 12px;")
        t_layout.addWidget(self.audio_label)
        
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #e74c3c; border: none; font-weight: bold; font-size: 12px;")
        self.warning_label.setWordWrap(True)
        t_layout.addWidget(self.warning_label)
        
        sidebar_layout.addWidget(telemetry_box)

        sidebar_layout.addSpacing(10)

        # --- Risk Log ---
        log_label = QLabel("Event Log")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        sidebar_layout.addWidget(log_label)

        self.risk_log = QTextEdit()
        self.risk_log.setReadOnly(True)
        self.risk_log.setStyleSheet("background-color: #34495e; color: #ecf0f1; border: none; font-size: 11px;")
        sidebar_layout.addWidget(self.risk_log)
        
        # Recalibrate Button
        self.btn_calib = QPushButton("CALIBRATE")
        self.btn_calib.setFixedHeight(50)
        self.btn_calib.setStyleSheet("""
            QPushButton {
                background-color: #e67e22; 
                color: white; 
                font-size: 14px; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.btn_calib.clicked.connect(self.recalibrate_request.emit)
        sidebar_layout.addWidget(self.btn_calib)
        
        sidebar_layout.addSpacing(10)
        
        # Quit Button
        btn_stop = QPushButton("END EXAM")
        btn_stop.setFixedHeight(50)
        btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                font-size: 14px; 
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_stop.clicked.connect(self.stop_request.emit)
        sidebar_layout.addWidget(btn_stop)
        
        sidebar_layout.addSpacing(20)
        
        layout.addWidget(sidebar)

    def reset_ui(self):
        """Resets all UI elements to default state"""
        self.risk_log.clear()
        self.calib_progress.setValue(0)
        self.calib_progress.hide()
        self.status_label.setText("STATUS: IDLE")
        self.status_label.setStyleSheet("color: #ecf0f1; border: 2px solid #bdc3c7; padding: 10px; border-radius: 5px;")
        self.pose_label.setText("Pose: -")
        self.audio_label.setText("Audio: -")
        self.warning_label.setText("")
        self.video_label.setText("Waiting for Camera...")
        
        # Reset Button to Start State
        self.btn_calib.setText("CALIBRATE")
        self.btn_calib.setEnabled(True)
        self.btn_calib.setStyleSheet("""
            QPushButton { background-color: #e67e22; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #d35400; }
        """)

    def update_frame(self, qt_image: QImage):
        """Slot to receive new frame from worker"""
        # Scale to fit label while keeping aspect ratio
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def log_message(self, message: str, color: str = "white"):
        """Log a generic message to the sidebar"""
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        html = f"<span style='color: grey'>[{timestamp}]</span> <span style='color: {color}'>{message}</span>"
        self.risk_log.append(html)

    def log_risk_event(self, event: RiskEvent):
        """Log a rich risk event to the sidebar"""
        color = "white"
        if event.risk_level.value == "HIGH": color = "#ff5555"
        elif event.risk_level.value == "MEDIUM": color = "#f1c40f"
        
        reasons_str = ", ".join(event.reasons)
        self.log_message(f"<b style='color: {color}'>{event.risk_level.value}</b>: {reasons_str}", "white")

    def update_status(self, text: str, color: str):
        """Update the sidebar status text"""
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; border: 2px solid {color}; padding: 10px; border-radius: 5px;")

    def update_stats(self, stats: dict):
        """Update telemetry labels and Button State"""
        if "yaw" in stats:
            self.pose_label.setText(f"Pose: Y:{stats['yaw']} P:{stats['pitch']}")
        
        if "audio_db" in stats:
            self.audio_label.setText(f"Audio: {stats['audio_db']}")
            
        if "warning" in stats:
            self.warning_label.setText(f"⚠ {stats['warning']}")
        else:
            self.warning_label.setText("")
        
        # Update Progress Bar
        if "calibration_progress" in stats:
            self.calib_progress.show()
            self.calib_progress.setValue(stats["calibration_progress"])
        else:
            self.calib_progress.hide()
            
        # Dynamic Button Logic
        # If we have pose data, we are likely monitoring or just finished calibration
        # Check explicit flag if available, else infer
        is_calibrating = stats.get("is_calibrating", False)
        
        # We need a way to know if we are successfully calibrated to show "RECALIBRATE"
        # The simplest way is: If we are receiving Head Pose stats, we are calibrated.
        # But we also receive them during calibration.
        # Let's rely on the absence of "warning" or explicit "calibrated" flag if we had one.
        # Actually, if we are in MONITORING mode (which sends stats), we are calibrated.
        # So "RECALIBRATE" is appropriate when monitoring.
        
        # Accessing the button relative to layout is hard, better to make it a class attribute
        if hasattr(self, "btn_calib"):
            if is_calibrating:
                # SHOW STOP BUTTON
                self.btn_calib.setText("STOP")
                self.btn_calib.setEnabled(True) # Enabled so we can stop it!
                self.btn_calib.setStyleSheet("""
                    QPushButton { background-color: #c0392b; color: white; border-radius: 5px; }
                    QPushButton:hover { background-color: #e74c3c; }
                """)
                # We need to disconnect old connections and connect to STOP?
                # This is tricky with PyQT signals. 
                # Better approach: Emit a generic 'action' signal and let MainWindow decide based on state?
                # OR: Logic in MainWindow to call correct worker method.
                # Let's keep it simple: The button emits 'recalibrate_request'.
                # MainWindow needs to know if it should call start or stop.
                # ACTUALLY: We can just have a separate signal for stop? or reuse.
                # Let's use a new signal `stop_calibration_request` and emit that if text is STOP.
                
                # To avoid complex signal logic here, let's keep it simple:
                # The visual update is just feedback. The button click handling needs to be smart.
                pass

            elif "yaw" in stats:
                self.btn_calib.setText("RECALIBRATE")
                self.btn_calib.setEnabled(True)
                self.btn_calib.setStyleSheet("""
                    QPushButton { background-color: #3498db; color: white; border-radius: 5px; }
                    QPushButton:hover { background-color: #2980b9; }
                """)
            else:
                self.btn_calib.setText("CALIBRATE")
                self.btn_calib.setEnabled(True)
                self.btn_calib.setStyleSheet("""
                    QPushButton { background-color: #e67e22; color: white; border-radius: 5px; }
                    QPushButton:hover { background-color: #d35400; }
                """)
