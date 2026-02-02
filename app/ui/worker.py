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
    log_signal = pyqtSignal(str, str) # (Message, Color) - New Log Channel
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.controller = SystemController()
        # Track previous state to log transitions
        self.prev_face_state = "IDLE" 
        
    def run(self):
        """Main CV Loop"""
        # Initialize Headless (no window creation here)
        self.log_signal.emit("Initializing System...", "#3498db")
        self.controller.initialize()
        self.controller.start()
        self.log_signal.emit("System Ready. Waiting for Calibration.", "#00FF00")
        
        while self.running:
            # 1. Logic Step
            step_result = self.controller.step()
            
            if step_result is None:
                self.msleep(10)
                continue
                
            frame, results, risk_event = step_result
            
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
                    
                # 3b. Emit Risk Event (Log)
                if risk_event:
                    self.risk_signal.emit(risk_event)

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
                        
                        # LOG STATE TRANSITIONS
                        # We don't have direct access to 'state' string in result, but we can infer
                        # Actually we can't easily infer "CALIBRATED" transition from just boolean is_calibrating
                        # We need the FaceDetector state.
                        # BUT, we can detect end of calibration:
                        if self.prev_face_state == "CALIBRATING" and not face.is_calibrating:
                             # Either Success or Failure?
                             # If we have yaw/pitch, it's likely success monitoring.
                             self.log_signal.emit("Calibration Successful!", "#00FF00")
                             self.prev_face_state = "MONITORING"
                        
                        elif not face.is_calibrating and self.prev_face_state == "IDLE":
                            # Maybe monitoring?
                            pass
                            
                        # Update tracker
                        if face.is_calibrating: 
                            self.prev_face_state = "CALIBRATING"
                        
                        # Pass calibration state to UI
                        stats["is_calibrating"] = face.is_calibrating
                        if face.is_calibrating:
                             stats["calibration_progress"] = int(face.calibration_progress * 100)
                        
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
        self.log_signal.emit("System Stopped.", "orange")

    def stop(self):
        self.running = False
        self.wait()
        
    def recalibrate(self):
        """Trigger calibration on the controller"""
        # This now triggers the STRICT DETACHMENT logic in controller
        self.log_signal.emit("Starting Calibration...", "#f39c12")
        self.controller.start_calibration()
        self.prev_face_state = "CALIBRATING"

    def stop_calibration(self):
        """Trigger stop calibration on controller"""
        self.log_signal.emit("Calibration Manual Stop.", "red")
        self.controller.stop_calibration()
        self.prev_face_state = "IDLE"
