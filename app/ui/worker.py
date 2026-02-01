import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
from app.core.system_controller import SystemController
from app.core.schemas import RiskLevel

class ProctorWorker(QThread):
    # Signals to update UI
    image_signal = pyqtSignal(QImage)
    status_signal = pyqtSignal(str, str) # (Status Text, Color Code)
    risk_signal = pyqtSignal(object) # RiskEvent object
    stats_signal = pyqtSignal(dict) # new generic stats channel
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.controller = SystemController()
        
    def run(self):
        """Main CV Loop"""
        # Initialize Headless (no window creation here)
        self.controller.initialize()
        self.controller.start()
        
        while self.running:
            # 1. Logic Step
            step_result = self.controller.step()
            
            if step_result is None:
                self.msleep(10)
                continue
                
            frame, results = step_result
            
            if frame is not None:
                # 2. Convert to Qt Image
                # OpenCV is BGR, Qt needs RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Create QImage from data (Zero Copy if possible, but keeping it safe)
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # emit emits a COPY of the image usually, safe for UI thread
                self.image_signal.emit(qt_image.copy())
                
                # 3. Emit Status Updates
                if self.controller.risk_engine and self.controller.risk_engine.current_risk_level:
                    level = self.controller.risk_engine.current_risk_level
                    color = "#00FF00" # Green
                    if level == RiskLevel.HIGH: color = "#FF0000"
                    elif level == RiskLevel.MEDIUM: color = "#FFFF00"
                    
                    self.status_signal.emit(f"RISK: {level.value}", color)

                # 4. Emit Rich Telemetry
                stats = {}
                # Extract Head Pose
                if "face" in results:
                    # Assuming list, take first face
                    faces = results["face"]
                    if faces and faces[0].face_present:
                        face = faces[0]
                        if face.yaw is not None:
                            stats["yaw"] = f"{face.yaw:.2f}"
                            stats["pitch"] = f"{face.pitch:.2f}"
                            stats["roll"] = f"{face.roll:.2f}"
                        
                        # Pass calibration state to UI?
                        stats["is_calibrating"] = face.is_calibrating
                        if face.calibration_warning:
                            stats["warning"] = face.calibration_warning

                # Extract Audio (if available)
                if "audio" in results and results["audio"]:
                     stats["audio_db"] = f"{results['audio'].decibels:.1f} dB"

                self.stats_signal.emit(stats)




            else:
                self.msleep(10) # Avoid busy loop if no camera
                
        # Cleanup
        self.controller.stop()

    def stop(self):
        self.running = False
        self.wait()
        
    def recalibrate(self):
        """Trigger calibration on the controller"""
        # This now triggers the STRICT DETACHMENT logic in controller
        self.controller.start_calibration()

    def stop_calibration(self):
        """Trigger stop calibration on controller"""
        self.controller.stop_calibration()
