from abc import ABC, abstractmethod
from typing import Any, List, Optional
from app.core.schemas import FrameData

class IDetector(ABC):
    """Marker interface for all detectors"""
    pass

class IVisionDetector(IDetector):
    @abstractmethod
    def detect(self, frame_data: FrameData) -> Any:
        pass

class IAudioDetector(IDetector):
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
        
    @abstractmethod
    def get_latest_sample(self) -> Any:
        pass

# Backward Compatibility
class IFaceDetector(IDetector):
    @abstractmethod
    def process(self, frame_data: FrameData) -> Any:
        pass

class IObjectDetector(IDetector):
    @abstractmethod
    def detect(self, frame_data: FrameData) -> Any:
        pass
