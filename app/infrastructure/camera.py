import cv2
import time
import threading
from typing import Optional
from app.config import settings
from app.infrastructure.logger import logger
from app.core.schemas import FrameData

class Camera:
    def __init__(self):
        self.camera_id = settings.camera.id
        self.cap = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Buffer
        self.last_frame: Optional[FrameData] = None
        self.frame_count = 0
        
    def start(self):
        logger.info(f"Opening camera {self.camera_id}...")
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.camera.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.camera.height)
        self.cap.set(cv2.CAP_PROP_FPS, settings.camera.fps)
        
        if not self.cap.isOpened():
            logger.error("Could not open camera!")
            raise RuntimeError("Camera open failed")
            
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        logger.info("Camera started.")

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame_count += 1
                    self.last_frame = FrameData(
                        frame_id=self.frame_count,
                        timestamp=time.time(),
                        frame=frame
                    )
            else:
                logger.warning("Failed to read frame")
                time.sleep(0.1)
                
    def read(self) -> Optional[FrameData]:
        with self.lock:
            if self.last_frame is None:
                return None
            # Return a copy or the same reference? 
            # For strictness, maybe copy, but for speed, reference.
            # Since we replace last_frame entirely in update, returning ref is safe enough 
            # IF the consumer processes it before it's overwritten or doesn't care.
            # Actually, the consumer needs the specific frame data. 
            return self.last_frame

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        logger.info("Camera stopped.")
