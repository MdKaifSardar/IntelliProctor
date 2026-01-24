from abc import ABC, abstractmethod
from typing import List, Any
from app.core.schemas import FrameData, DetectionResult, FaceResult

class IObjectDetector(ABC):
    @abstractmethod
    def detect(self, frame_data: FrameData) -> List[DetectionResult]:
        """Detect objects in the frame."""
        pass

class IFaceDetector(ABC):
    @abstractmethod
    def process(self, frame_data: FrameData) -> List[FaceResult]:
        """Process face landmarks and pose."""
        pass
