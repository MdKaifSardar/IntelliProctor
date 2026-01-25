from typing import List, Optional
import time
from app.core.schemas import AnalysisSignal, RiskEvent, RiskLevel, BehaviorType
from app.config import settings

class RiskEngine:
    def __init__(self):
        self.last_alert_time = 0
        self.current_risk_level = RiskLevel.LOW
        self.accumulated_score = 0.0
        
    def process(self, signals: List[AnalysisSignal]) -> Optional[RiskEvent]:
        current_time = time.time()
        
        if not signals:
            # Decay score over time if no signals? (Optional, skipping for simplicity)
            self.current_risk_level = RiskLevel.LOW
            return None
            
        # 1. Calculate Frame Score
        frame_score = 0.0
        reasons = set()
        
        for signal in signals:
            reasons.add(signal.details)
            
            if signal.behavior_type == BehaviorType.PHONE_DETECTED:
                frame_score += settings.risk.weight_phone
            elif signal.behavior_type == BehaviorType.PERSON_LIMIT_VIOLATION:
                frame_score += settings.risk.weight_multiple_faces
            elif signal.behavior_type == BehaviorType.FACE_NOT_VISIBLE:
                frame_score += settings.risk.weight_no_face
            elif signal.behavior_type == BehaviorType.LOOKING_AWAY:
                frame_score += settings.risk.weight_gaze
            elif signal.behavior_type == BehaviorType.PITCH_VIOLATION:
                frame_score += settings.risk.weight_pitch
            elif signal.behavior_type == BehaviorType.AUDIO_DETECTED:
                frame_score += settings.risk.weight_audio
            elif signal.behavior_type == BehaviorType.HEADPHONE_DETECTED:
                frame_score += settings.risk.weight_headphone
                
        # 2. Determine Risk Level
        # Simple thresholding
        if frame_score >= 0.8:
            new_level = RiskLevel.HIGH
        elif frame_score >= 0.4:
            new_level = RiskLevel.MEDIUM
        else:
            new_level = RiskLevel.LOW
            
        self.current_risk_level = new_level
        
        # 3. Cooldown check for Events
        if new_level != RiskLevel.LOW:
            if current_time - self.last_alert_time > settings.risk.alert_cooldown:
                self.last_alert_time = current_time
                return RiskEvent(
                    timestamp=current_time,
                    risk_level=new_level,
                    reasons=list(reasons)
                )
        
        return None
