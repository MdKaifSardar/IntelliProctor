from collections import deque
from typing import List, Optional
from app.core.schemas import FaceResult, DetectionResult, AnalysisSignal, BehaviorType, RiskLevel
from app.config import settings

class BehaviorAnalyzer:
    def __init__(self):
        self.history_size = 30 # keep 1 second of history at 30fps
        self.face_history = deque(maxlen=self.history_size)
        self.object_history = deque(maxlen=self.history_size)
        
        # State Counters
        self.frames_no_face = 0
        self.frames_looking_away = 0
        
    def _analyze_face(self, face_results: List[FaceResult]) -> List[AnalysisSignal]:
        signals = []
        
        # Check presence
        if not face_results or not face_results[0].face_present:
            self.frames_no_face += 1
            if self.frames_no_face > settings.risk.max_frames_missing_face:
                 signals.append(AnalysisSignal(
                     behavior_type=BehaviorType.FACE_NOT_VISIBLE,
                     detected_at=0, # Timestamp to be filled by caller or now
                     details=f"Face missing for {self.frames_no_face} frames",
                     severity=RiskLevel.MEDIUM
                 ))
        else:
            self.frames_no_face = 0 # Reset
            
            # Check Gaze (only if face is present)
            face = face_results[0]
            # Thresholds for looking away (normalized -1 to 1)
            # 0.4 roughly corresponds to 30-40 degrees if we normalized by 90
            # Thresholds for looking away (normalized -1 to 1)
            # 0.25 roughly corresponds to ~22 degrees (Sensitivity Increased)
            THRESHOLD = 0.22 
            if abs(face.yaw) > THRESHOLD or abs(face.pitch) > THRESHOLD:
                self.frames_looking_away += 1
                if self.frames_looking_away > settings.risk.max_frames_looking_away:
                     signals.append(AnalysisSignal(
                         behavior_type=BehaviorType.LOOKING_AWAY,
                         detected_at=0,
                         details=f"Extensive looking away ({face.yaw:.2f}, {face.pitch:.2f})",
                         severity=RiskLevel.LOW
                     ))
            else:
                self.frames_looking_away = 0
                
        return signals

    def _analyze_objects(self, detections: List[DetectionResult]) -> List[AnalysisSignal]:
        signals = []
        
        person_count = 0
        
        for det in detections:
            if det.label == "person":
                person_count += 1
            
            if det.label == "cell phone":
                signals.append(AnalysisSignal(
                    behavior_type=BehaviorType.PHONE_DETECTED,
                    detected_at=0,
                    details="Mobile Phone detected",
                    severity=RiskLevel.HIGH
                ))
        
        # Note: YOLO often counts the user as a person. 
        # So we expect 1 person. If > 1, multiple people.
        # But if face is missing, we might have 0 people? 
        # Logic: If > 1 person seen -> Multiple people risk
        if person_count > 1:
            signals.append(AnalysisSignal(
                behavior_type=BehaviorType.PERSON_LIMIT_VIOLATION,
                detected_at=0,
                details=f"Multiple people detected ({person_count})",
                severity=RiskLevel.HIGH
            ))
            
        return signals

    def analyze(self, timestamp: float, face_results: List[FaceResult], object_results: List[DetectionResult]) -> List[AnalysisSignal]:
        signals = []
        
        # Analyze Face
        face_signals = self._analyze_face(face_results)
        signals.extend(face_signals)
        
        # Analyze Objects
        obj_signals = self._analyze_objects(object_results)
        signals.extend(obj_signals)
        
        # Stamp time
        for s in signals:
            s.detected_at = timestamp
            
        return signals
