from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Optional, Tuple, Any
import numpy as np

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class BehaviorType(str, Enum):
    LOOKING_AWAY = "LOOKING_AWAY"
    PHONE_DETECTED = "PHONE_DETECTED"
    PERSON_LIMIT_VIOLATION = "PERSON_LIMIT_VIOLATION"
    FACE_NOT_VISIBLE = "FACE_NOT_VISIBLE"
    AUDIO_DETECTED = "AUDIO_DETECTED" # Future proofing

class FrameData(BaseModel):
    frame_id: int
    timestamp: float
    frame: Any  # numpy array, but Any to avoid pydantic validation overhead on image data
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DetectionResult(BaseModel):
    label: str
    confidence: float
    box: Tuple[int, int, int, int] # x1, y1, x2, y2

class FaceResult(BaseModel):
    face_present: bool
    landmarks: Optional[List[Tuple[float, float]]] = None # Normalized coordinates
    yaw: Optional[float] = None
    pitch: Optional[float] = None
    roll: Optional[float] = None

class AnalysisSignal(BaseModel):
    behavior_type: BehaviorType
    detected_at: float
    details: str
    severity: RiskLevel

class RiskEvent(BaseModel):
    timestamp: float
    risk_level: RiskLevel
    reasons: List[str]
