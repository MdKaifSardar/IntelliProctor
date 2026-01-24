import os
from pydantic import BaseModel, Field
from typing import Tuple

class CameraConfig(BaseModel):
    id: int = Field(0, description="Camera Device ID")
    width: int = Field(1280, description="Capture Width")
    height: int = Field(720, description="Capture Height")
    fps: int = Field(30, description="Capture FPS")

class FaceDetectorConfig(BaseModel):
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    face_mesh_refine_landmarks: bool = True

class ObjectDetectorConfig(BaseModel):
    model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    target_classes: list[int] = Field(
        default=[0, 67, 73], 
        description="COCO class IDs: 0=person, 67=cell phone, 73=laptop (optional adjustment needed)"
        # Note: YOLO COCO: 0:person, 67:cell phone. 
        # Check specific model classes. 67 is cell phone in COCO.
    )

class RiskConfig(BaseModel):
    # Cooldowns in seconds
    alert_cooldown: float = 2.0
    
    # Thresholds (frames)
    max_frames_missing_face: int = 30  # ~1 sec at 30fps
    max_frames_looking_away: int = 3  # ~0.1 sec - nearly instant
    
    # Weights for scoring (0.0 to 1.0)
    weight_phone: float = 1.0     # Critical
    weight_multiple_faces: float = 0.8 # High
    weight_no_face: float = 0.6   # Medium
    weight_gaze: float = 0.5      # Solid Medium Risk (was 0.4)

class AppConfig(BaseModel):
    camera: CameraConfig = Field(default_factory=CameraConfig)
    face_detector: FaceDetectorConfig = Field(default_factory=FaceDetectorConfig)
    object_detector: ObjectDetectorConfig = Field(default_factory=ObjectDetectorConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "PROCTOR_"

# Global Config Instance
settings = AppConfig()
