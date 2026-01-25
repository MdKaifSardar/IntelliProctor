import cv2
import numpy as np
from typing import List
from app.core.schemas import FrameData, DetectionResult, FaceResult, RiskEvent, RiskLevel
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
            cv2.putText(frame, f"{det.label} {det.confidence:.2f}", (x1, y1 - 10),
                        self.font, 0.5, color, 1)

    def draw_face_info(self, frame: np.ndarray, face_results: List[FaceResult]):
        if not face_results:
            cv2.putText(frame, "NO FACE", (50, 50), self.font, 1, (0, 0, 255), 2)
            return

        for face in face_results:
            if face.face_present:
                 # Draw simple gaze indicator if pose available
                if face.yaw is not None:
                    status = "Frontal"
                    if abs(face.yaw) > settings.face.yaw_threshold: status = "Side Looking"
                    
                    # Main Status
                    cv2.putText(frame, f"Head: {status}", (30, 80), self.font, 0.7, (255, 255, 0), 2)
                    
                    # Details (Y=Yaw, P=Pitch, R=Roll)
                    stats = f"Y:{face.yaw:.2f} P:{face.pitch:.2f} R:{face.roll:.2f}"
                    cv2.putText(frame, stats, (30, 110), self.font, 0.5, (200, 200, 200), 1)

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
                            # Standard mesh (Small White Dot, sparse drawing for perf?)
                            # Drawing all 478 points might be busy, but let's do it as requested "dots layout"
                            # Optimization: Draw every n-th point to avoid clutter or draw all if specific visuals needed
                            if idx % 5 == 0: # Light mesh
                                cv2.circle(frame, (x, y), 1, (200, 200, 200), -1)

    def draw_risk(self, frame: np.ndarray, risk_event: RiskEvent):
        color = self.colors.get(risk_event.risk_level, (255, 255, 255))
        
        # Risk Header
        cv2.putText(frame, f"RISK: {risk_event.risk_level.value}", (10, 30), 
                    self.font, 1, color, 2)
        
        # Reasons
        y_offset = 60
        for reason in risk_event.reasons:
            cv2.putText(frame, f"- {reason}", (10, y_offset), 
                        self.font, 0.6, color, 1)
            y_offset += 25

    def render(self, frame_data: FrameData, detections: List, faces: List, risk: RiskEvent) -> np.ndarray:
        # Work on a copy to avoid corrupting the original frame data if used elsewhere
        vis_frame = frame_data.frame.copy()
        
        self.draw_detections(vis_frame, detections)
        self.draw_face_info(vis_frame, faces)
        if risk:
            self.draw_risk(vis_frame, risk)
            
        return vis_frame
