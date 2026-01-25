from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Optional, Tuple, Any

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class BehaviorType(str, Enum):
    LOOKING_AWAY = "LOOKING_AWAY"     # Left/Right
    PITCH_VIOLATION = "PITCH_VIOLATION" # Up/Down
    PHONE_DETECTED = "PHONE_DETECTED"
    HEADPHONE_DETECTED = "HEADPHONE_DETECTED"
    PERSON_LIMIT_VIOLATION = "PERSON_LIMIT_VIOLATION"
    FACE_NOT_VISIBLE = "FACE_NOT_VISIBLE"
    AUDIO_DETECTED = "AUDIO_DETECTED"

class FrameData(BaseModel):
    frame_id: int
    timestamp: float
    frame: Any  # numpy array
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DetectionResult(BaseModel):
    label: str
    confidence: float
    box: Tuple[int, int, int, int] # x1, y1, x2, y2

class FaceResult(BaseModel):
    face_present: bool
    landmarks: Optional[Any] = None 
    yaw: Optional[float] = None
    pitch: Optional[float] = None
    roll: Optional[float] = None

class AudioResult(BaseModel):
    speech_detected: bool
    rms_level: float
    decibels: float

class AnalysisSignal(BaseModel):
    behavior_type: BehaviorType
    detected_at: float
    details: str
    severity: RiskLevel

class RiskEvent(BaseModel):
    timestamp: float
    risk_level: RiskLevel
    reasons: List[str]
