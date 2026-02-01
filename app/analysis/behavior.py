from collections import deque
from typing import List, Optional, Any, Dict
from app.core.schemas import FaceResult, DetectionResult, AnalysisSignal, BehaviorType, RiskLevel
from app.config import settings

class BehaviorAnalyzer:
    def __init__(self):
        self.history_size = 30 # keep 1 second of history at 30fps
        # State Counters
        self.frames_no_face = 0
        self.frames_looking_away = 0
        self.frames_pitch_violation = 0

        # Handlers Map: Maps "source_name" to "handler_method"
        self._handlers = {
            "face": self._analyze_face,
            "object": self._analyze_objects,
            "audio": self._analyze_audio
        }
        
    def register_handler(self, source: str, handler_func):
        """Allow dynamic registration of new analysis modules"""
        self._handlers[source] = handler_func

    def _analyze_face(self, face_results: List[FaceResult]) -> List[AnalysisSignal]:
        signals = []
        if not face_results: 
            return signals
            
        # Check presence
        if not face_results[0].face_present:
            self.frames_no_face += 1
            if self.frames_no_face > settings.risk.max_frames_missing_face:
                 signals.append(AnalysisSignal(
                     behavior_type=BehaviorType.FACE_NOT_VISIBLE,
                     detected_at=0,
                     details=f"Face missing for {self.frames_no_face} frames",
                     severity=RiskLevel.MEDIUM
                 ))
        else:
            self.frames_no_face = 0 # Reset
            
            face = face_results[0]
            
            # Check Gaze (Left/Right)
            YAW_THRESHOLD = settings.face.yaw_threshold
            if abs(face.yaw) > YAW_THRESHOLD:
                self.frames_looking_away += 1
                if self.frames_looking_away > settings.risk.max_frames_looking_away:
                     signals.append(AnalysisSignal(
                         behavior_type=BehaviorType.LOOKING_AWAY,
                         detected_at=0,
                         details=f"Extensive looking away ({face.yaw:.2f})",
                         severity=RiskLevel.LOW
                     ))
            else:
                self.frames_looking_away = 0
                
            # Check Pitch (Up/Down)
            PITCH_THRESHOLD = settings.face.pitch_threshold
            if abs(face.pitch) > PITCH_THRESHOLD:
                self.frames_pitch_violation += 1
                if self.frames_pitch_violation > settings.risk.max_frames_pitch_violation:
                     signals.append(AnalysisSignal(
                         behavior_type=BehaviorType.PITCH_VIOLATION,
                         detected_at=0,
                         details=f"Looking Up/Down detected ({face.pitch:.2f})",
                         severity=RiskLevel.MEDIUM
                     ))
            else:
                 self.frames_pitch_violation = 0
                
        return signals

    def _analyze_objects(self, detections: List[DetectionResult]) -> List[AnalysisSignal]:
        signals = []
        person_count = 0
        
        for det in detections:
            label = det.label.lower()
            
            if label == "person":
                person_count += 1
            elif label in settings.objects.forbidden_objects:
                signals.append(AnalysisSignal(
                    behavior_type=BehaviorType.OBJECT_DETECTED,
                    detected_at=0,
                    details=f"Forbidden object detected: {det.label}",
                    severity=RiskLevel.HIGH
                ))
        
        if person_count > 1:
            signals.append(AnalysisSignal(
                behavior_type=BehaviorType.PERSON_LIMIT_VIOLATION,
                detected_at=0,
                details=f"Multiple people detected ({person_count})",
                severity=RiskLevel.HIGH
            ))
            
        return signals

    def _analyze_audio(self, audio_result: Any) -> List[AnalysisSignal]:
        signals = []
        if audio_result and audio_result.speech_detected:
            signals.append(AnalysisSignal(
                behavior_type=BehaviorType.AUDIO_DETECTED,
                detected_at=0,
                details=f"Audio/Speech Detected ({audio_result.decibels:.1f} dB)",
                severity=RiskLevel.HIGH
            ))
        return signals

    def analyze(self, timestamp: float, results_map: Dict[str, Any]) -> List[AnalysisSignal]:
        """
        Generic analysis entry point.
        Iterates through the results_map and dispatches to registered handlers.
        """
        signals = []
        
        for source, data in results_map.items():
            if source in self._handlers and data is not None:
                new_signals = self._handlers[source](data)
                signals.extend(new_signals)
        
        # Stamp time
        for s in signals:
            s.detected_at = timestamp
            
        return signals
