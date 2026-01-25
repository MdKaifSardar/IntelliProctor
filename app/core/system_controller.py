import time
from typing import Dict, Any, Optional
from app.config import settings
from app.infrastructure.logger import logger
from app.infrastructure.camera import Camera
from app.infrastructure.visualizer import Visualizer
from app.detectors.face_detector import FaceDetector
from app.detectors.object_detector import ObjectDetector
from app.detectors.audio_detector import AudioDetector
from app.analysis.behavior import BehaviorAnalyzer
from app.analysis.risk_engine import RiskEngine
from app.core.schemas import FaceResult, DetectionResult, AudioResult

class SystemController:
    """
    Central control unit.
    - Manages lifecycle of all sub-modules.
    - Orchestrates data flow.
    - Applies configuration.
    """
    def __init__(self):
        self.camera: Optional[Camera] = None
        self.detectors: Dict[str, Any] = {}
        self.behavior: Optional[BehaviorAnalyzer] = None
        self.risk_engine: Optional[RiskEngine] = None
        self.visualizer: Optional[Visualizer] = None
        
    def initialize(self):
        logger.info("Initializing System Controller...")
        
        # 1. Core Hardware
        self.camera = Camera()
        self.visualizer = Visualizer()
        
        # 2. Logic Engines
        self.behavior = BehaviorAnalyzer()
        self.risk_engine = RiskEngine()
        
        # 3. Dynamic Detectors
        active = settings.active_modules
        
        if "face" in active:
            logger.info("Loading Face Module...")
            self.detectors["face"] = FaceDetector()
            
        if "object" in active:
            logger.info("Loading Object Module...")
            self.detectors["object"] = ObjectDetector()
            
        if "audio" in active:
            logger.info("Loading Audio Module...")
            # For audio, we need to explicitly start it
            self.detectors["audio"] = AudioDetector()

    def start(self):
        if self.camera:
            self.camera.start()
        
        if "audio" in self.detectors:
            self.detectors["audio"].start()
            
    def stop(self):
        if "audio" in self.detectors:
            self.detectors["audio"].stop()
            
        if self.camera:
            self.camera.stop()

    def step(self) -> Optional[Any]:
        """
        Executes one TICK of the system loop.
        Returns the visualized frame or None.
        """
        if not self.camera:
            return None
            
        # 1. Read Inputs
        frame_data = self.camera.read()
        if frame_data is None:
            return None
            
        # 2. Run Detectors
        face_results = []
        object_results = []
        audio_result = None
        
        if "face" in self.detectors:
            face_results = self.detectors["face"].process(frame_data)
            
        if "object" in self.detectors:
            object_results = self.detectors["object"].detect(frame_data)
            
        if "audio" in self.detectors:
            audio_result = self.detectors["audio"].get_latest_sample()

        # 3. Analyze Behavior
        results_map = {
            "face": face_results,
            "object": object_results,
            "audio": audio_result
        }
        
        signals = self.behavior.analyze(
            timestamp=frame_data.timestamp,
            results_map=results_map
        )
        
        # 4. Determine Risk
        risk_event = self.risk_engine.process(signals)
        
        if risk_event:
            logger.warning(f"RISK EVENT: {risk_event.risk_level.value} - {risk_event.reasons}")
            
        # 5. Visualize
        # Need to adapt visualizer to likely accept audio info (optional)
        vis_frame = self.visualizer.render(
            frame_data,
            object_results,
            face_results,
            risk_event
        )
        
        # Draw Audio Info manually if needed or update visualizer
        if audio_result and audio_result.speech_detected:
             import cv2
             cv2.putText(vis_frame, f"AUDIO: {audio_result.decibels:.1f}dB", (10, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        elif audio_result:
             import cv2
             cv2.putText(vis_frame, f"AUDIO: {audio_result.decibels:.1f}dB", (10, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

        return vis_frame
