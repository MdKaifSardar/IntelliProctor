import os
from pydantic import BaseModel, Field
from typing import List, Set

class CameraConfig(BaseModel):
    id: int = Field(0, description="Camera Device ID")
    width: int = Field(1280, description="Capture Width")
    height: int = Field(720, description="Capture Height")
    fps: int = Field(30, description="Capture FPS")

class FaceDetectorConfig(BaseModel):
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    face_mesh_refine_landmarks: bool = True
    
    # Sensitivity (Normalized -1.0 to 1.0)
    yaw_threshold: float = 0.20   # Left/Right
    pitch_threshold: float = 0.20 # Up/Down
    visualize_landmarks: bool = True # Show face mesh

class ObjectDetectorConfig(BaseModel):
    model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    # targeted classes: person (0), cell phone (67)
    # Note: Headphones not standard in COCO, we will simulate or require custom model
    target_classes: list[int] = [0, 67] 
    forbidden_objects: list[str] = ["cell phone", "mobile phone", "headphone", "headset"] # Labels to trigger High Risk 

class AudioConfig(BaseModel):
    enabled: bool = True
    threshold_rms: float = 0.01 # Sensitivity for noise
    sample_rate: int = 16000
    block_size: int = 1024

class RiskConfig(BaseModel):
    # Cooldowns in seconds
    alert_cooldown: float = 2.0
    
    # Thresholds (frames)
    max_frames_missing_face: int = 30  # ~1 sec
    max_frames_looking_away: int = 3   # ~0.1 sec (Yaw)
    max_frames_pitch_violation: int = 5 # ~0.15 sec (Pitch)
    
    # Weights for scoring (0.0 to 1.0)
    weight_phone: float = 1.0     
    weight_multiple_faces: float = 0.8
    weight_no_face: float = 0.6   
    weight_gaze: float = 0.5      
    weight_pitch: float = 0.5     # New
    weight_audio: float = 0.7     # New
    weight_headphone: float = 0.9 # New

class AppConfig(BaseModel):
    # Dynamic Module Control
    active_modules: Set[str] = Field(
        default_factory=lambda: {"face", "object", "audio"}
    )
    
    camera: CameraConfig = Field(default_factory=CameraConfig)
    face: FaceDetectorConfig = Field(default_factory=FaceDetectorConfig)
    objects: ObjectDetectorConfig = Field(default_factory=ObjectDetectorConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "PROCTOR_"

settings = AppConfig()
