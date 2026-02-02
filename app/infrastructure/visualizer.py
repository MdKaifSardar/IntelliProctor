import cv2
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from app.core.schemas import FrameData, DetectionResult, FaceResult, RiskEvent, RiskLevel, AudioResult
from app.config import settings

class Visualizer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.colors = {
            RiskLevel.LOW: (0, 255, 0),    # Green
            RiskLevel.MEDIUM: (0, 255, 255), # Yellow
            RiskLevel.HIGH: (0, 0, 255)    # Red
        }
    
    def draw_detections(self, frame: np.ndarray, detections: List[DetectionResult]):
        for det in detections:
            x1, y1, x2, y2 = det.box
            color = (0, 0, 255) if det.label == "cell phone" else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            # No Text

    def draw_face_info(self, frame: np.ndarray, face_results: List[FaceResult]):
        if not face_results:
            return

        for face in face_results:
            if face.face_present:
                # Draw Calibration Status (Box only)
                self._draw_calibration_status(frame, face)

                # Draw Landmarks if enabled
                if settings.face.visualize_landmarks and face.landmarks:
                    h, w, _ = frame.shape
                    
                    # Key points to highlight (Nose, Chin, Left Eye, Right Eye, Mouth L, Mouth R)
                    key_indices = [1, 152, 33, 263, 61, 291]
                    
                    for idx, lm in enumerate(face.landmarks):
                        x, y = int(lm.x * w), int(lm.y * h)
                        
                        if idx in key_indices:
                            # Highlight key points (Larger Yellow Dot)
                            cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)
                        else:
                            pass

    def draw_risk(self, frame: np.ndarray, risk_event: RiskEvent):
        # User requested NO text on camera feed for risk.
        # This is now handled entirely by the Sidebar UI.
        pass

    def render(self, frame_data: FrameData, 
              object_results: List[DetectionResult], 
              face_results: List[FaceResult],
              risk_event: Optional[RiskEvent],
              audio_result: Optional[AudioResult] = None) -> np.ndarray:
              
        image = frame_data.frame.copy()
        
        # 1. Draw Object Detections
        self.draw_detections(image, object_results)
            
        # 2. Draw Face Results & Landmarks
        self.draw_face_info(image, face_results)
            
        # 3. Draw Risk Event (Top Banner)
        if risk_event:
            self.draw_risk(image, risk_event)

        # 4. Draw Audio Status
        if audio_result:
            self._draw_audio_info(image, audio_result)
            
        return image

    def _draw_audio_info(self, image, audio_result: AudioResult):
        if audio_result.speech_detected:
            # Visual cue only (Red Border)
            h, w = image.shape[:2]
            cv2.rectangle(image, (0, 0), (w, h), (0, 0, 255), 4)



    def _draw_calibration_status(self, frame, face_res):
        """Draws feedback during calibration"""
        h, w = frame.shape[:2]
        
        if face_res.calibration_warning:
            # Big Red Warning
            cv2.putText(frame, face_res.calibration_warning, (w//2 - 250, h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                       
        if face_res.is_calibrating:
            # Blue Progress Bar / Status
            cv2.putText(frame, "CALIBRATING... LOOK STRAIGHT", (w//2 - 200, h//2 - 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
            # Indeterminate bar
            cv2.rectangle(frame, (w//2 - 100, h//2 + 20), (w//2 + 100, h//2 + 40), (255, 0, 0), -1)
