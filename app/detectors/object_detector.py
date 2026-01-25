from ultralytics import YOLO
from typing import List
from app.core.interfaces import IObjectDetector
from app.core.schemas import FrameData, DetectionResult
from app.config import settings

class ObjectDetector(IObjectDetector):
    def __init__(self):
        # Load model (will auto-download if not present)
        self.model = YOLO(settings.objects.model_path)
        self.target_classes = set(settings.objects.target_classes)
        self.names = self.model.names if hasattr(self.model, 'names') else {}
        
    def detect(self, frame_data: FrameData) -> List[DetectionResult]:
        # Run inference
        results = self.model.predict(
            frame_data.frame, 
            verbose=False, 
            conf=settings.objects.confidence_threshold,
            classes=list(self.target_classes) # Filter at inference level if possible
        )
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                if cls_id not in self.target_classes:
                    continue
                    
                label = self.names.get(cls_id, str(cls_id))
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = map(int, xyxy)
                
                detections.append(DetectionResult(
                    label=label,
                    confidence=conf,
                    box=(x1, y1, x2, y2)
                ))
                
        return detections
