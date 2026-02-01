import time
import cv2
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
            # Warmup to prevent first-inference lag
            logger.info("Warming up Face Module...")
            self.detectors["face"].warmup()
            
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
        Returns (visualized frame, results_map)
        """
        if not self.camera:
            return None
            
        # 1. Read Inputs
        frame_data = self.camera.read()
        if frame_data is None:
            return None
            
        # State Machine Flags
        # These should be class attributes initialized in __init__
        # Adding them here dynamically for now if missing, but ideally in __init__
        if not hasattr(self, "calibration_in_progress"): self.calibration_in_progress = False
        if not hasattr(self, "is_monitoring"): self.is_monitoring = False

        vis_frame = None
        results_map = {}

        # --- STATE 1: IDLE (Uncalibrated) ---
        if not self.is_monitoring and not self.calibration_in_progress:
            # Zero Computation Mode
            # Just pass through the video feed with a message
            vis_frame = frame_data.frame.copy()
            # We can rely on visualizer to draw "Not Calibrated" if we pass empty results, 
            # or just do nothing. Visualizer might be confused by None results.
            # Let's use visualizer to strictly render safety message.
            vis_frame = self.visualizer.render(frame_data, [], [], None, None)
            return vis_frame, {}

        # --- STATE 2: CALIBRATING ---
        if self.calibration_in_progress:
            face_results = []
            if "face" in self.detectors:
                face_detector = self.detectors["face"]
                face_results = face_detector.process(frame_data)
                
                # Check Face Detector State
                fd_state = getattr(face_detector, "state", "IDLE")
                
                if fd_state == "CALIBRATED":
                    # SUCCESS: Switch to Monitoring
                    logger.info("Calibration Successful. Starting Monitoring.")
                    self.calibration_in_progress = False
                    self.is_monitoring = True
                    
                elif fd_state == "IDLE" and self.calibration_in_progress:
                     # This means it failed (Anti-Cheat check or lost face)
                     logger.info("Calibration Failed. Resetting to IDLE.")
                     self.calibration_in_progress = False
                     self.is_monitoring = False
                     # Visualizer will show failure message if detector set one

            # Render Logic for Calibration
            vis_frame = self.visualizer.render(frame_data, [], face_results, None, None)
            
            # Pass results so UI can see "is_calibrating" flag
            return vis_frame, {"face": face_results}

        # --- STATE 3: MONITORING (Calibrated) ---
        if self.is_monitoring:
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
            
            signals = self.behavior.analyze(frame_data.timestamp, results_map)
            
            # 4. Determine Risk
            risk_event = self.risk_engine.process(signals)
            
            if risk_event:
                logger.warning(f"RISK EVENT: {risk_event.risk_level.value} - {risk_event.reasons}")
                
            # 5. Visualize
            vis_frame = self.visualizer.render(
                frame_data,
                object_results,
                face_results,
                risk_event,
                audio_result
            )

            return vis_frame, results_map
            

        return None, {}

    def start_calibration(self):
        """
        Triggers the calibration process.
        Detaches all other modules by setting is_monitoring = False.
        """
        logger.info("Starting Calibration Process... Detaching Modules.")
        
        # 1. Reset Flags
        self.is_monitoring = False
        self.calibration_in_progress = True
        
        # 2. Trigger Face Detector's internal logic
        if "face" in self.detectors:
            self.detectors["face"].start_calibration()

    def stop_calibration(self):
        """
        Manually cancels the calibration process.
        Resets everything to IDLE.
        """
        logger.info("Stopping Calibration Process (Manual or Failed).")
        self.calibration_in_progress = False
        self.is_monitoring = False
        
        # Reset Face Detector State
        if "face" in self.detectors:
            self.detectors["face"].state = "IDLE"
            self.detectors["face"].is_calibrating = False
            self.detectors["face"].calibration_warning = None


