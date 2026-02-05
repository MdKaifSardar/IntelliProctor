import time
import cv2
from typing import Dict, Any, Optional, Tuple
from app.config import settings
from app.infrastructure.logger import logger
from app.infrastructure.camera import Camera
from app.infrastructure.visualizer import Visualizer
from app.detectors.face_detector import FaceDetector
from app.detectors.object_detector import ObjectDetector
from app.detectors.audio_detector import AudioDetector
from app.analysis.behavior import BehaviorAnalyzer
from app.analysis.risk_engine import RiskEngine
from app.analysis.gaze_calibrator import GazeCalibrator # NEW
from app.core.schemas import FaceResult, DetectionResult, AudioResult, FrameData, RiskEvent

class SystemController:
    """
    Central control unit.
    - Manages lifecycle of all sub-modules.
    - Orchestrates data flow.
    - Applies configuration.
    """
    def __init__(self):
        self.detectors: Dict[str, Any] = {}
        self.behavior: BehaviorAnalyzer = None
        self.risk_engine: RiskEngine = None
        self.gaze_calibrator = GazeCalibrator() # NEW
        
        self.camera = None
        self.visualizer = Visualizer()
        
        # State
        self.is_monitoring = False
        self.calibration_in_progress = False
        
    def initialize(self):
        logger.info("Initializing System Controller...")
        
        # 1. Core Hardware
        self.camera = Camera()
        # self.visualizer = Visualizer() # Moved to __init__
        
        # 2. Logic Engines
        # self.behavior = BehaviorAnalyzer() # Moved to __init__
        # self.risk_engine = RiskEngine() # Moved to __init__
        
        # 3. Dynamic Detectors
        active_modules = settings.active_modules
        
        if "face" in active_modules:
            logger.info("Loading Face Module...")
            try:
                self.detectors["face"] = FaceDetector()
                # Warmup to prevent first-inference lag
                logger.info("Warming up Face Module...")
                self.detectors["face"].warmup()
            except Exception as e:
                logger.error(f"Failed to load Face Module: {e}")
            
        if "object" in active_modules:
            logger.info("Loading Object Module...")
            self.detectors["object"] = ObjectDetector()
            
        if "audio" in active_modules:
            logger.info("Loading Audio Module...")
            # For audio, we need to explicitly start it
            self.detectors["audio"] = AudioDetector()

        # Initialize Logic Engines
        self.behavior = BehaviorAnalyzer()
        self.risk_engine = RiskEngine()
        
        # Register handlers
        self.behavior.register_handler("face", self.behavior._analyze_face)
        self.behavior.register_handler("object", self.behavior._analyze_objects)
        self.behavior.register_handler("audio", self.behavior._analyze_audio)
        
        logger.info("System Initialized.")

    def start(self):
        if self.camera:
            self.camera.start()
        
        if "audio" in self.detectors:
            self.detectors["audio"].start()
            
    def stop(self):
        # Stop Hardware
        if self.camera:
            self.camera.stop()
            
        # Reset Logic Engines
        if self.behavior:
            self.behavior.reset()
        
        if self.risk_engine:
            self.risk_engine.reset()
            
        # Reset Calibrator
        self.gaze_calibrator.reset()
            
        # Reset all detectors to ensure fresh start next run
        if "face" in self.detectors:
             self.detectors["face"].reset()
             
        if "audio" in self.detectors:
            self.detectors["audio"].stop()
            
        # if self.camera: # Already handled above
        #     self.camera.stop()
            
        # # Reset Logic Engines # Already handled above
        # if self.behavior:
        #     self.behavior.reset()
            
        # if self.risk_engine:
        #     self.risk_engine.reset()

    def step(self) -> Tuple[Any, dict, Optional[RiskEvent]]:
        """
        Main Loop Step.
        1. Read Frame.
        2. Detect (Face) always if calibrating or monitoring.
        3. Calibrate (GazeCalibrator).
        4. Logic (Behavior/Risk) ONLY if monitoring.
        """
        if not self.camera:
            return None, {}, None

        # 1. Read Inputs
        frame_data = self.camera.read()
        if frame_data is None:
            return None, {}, None

        results = {}
        
        # 0. Fast Fail: If not monitoring and not calibrating, do nothing (just frame)
        if not self.is_monitoring and not self.calibration_in_progress:
            # We assume IDLE state, return frame with "Waiting" status effectively
            return self.visualizer.render(frame_data, [], [], None, None), {}, None
            
        # 1. Face Detection (Always needed for both Calib and Monitor)
        face_results = []
        if "face" in self.detectors:
            raw_results = self.detectors["face"].process(frame_data)
            
            # PIPE THROUGH GAZE CALIBRATOR
            for res in raw_results:
                if res.face_present:
                    # Provide Raw to Calibrator
                    cal_yaw, cal_pitch = self.gaze_calibrator.update(res.yaw, res.pitch)
                    
                    # Update Result with Calibrated Data + Status
                    res.yaw = cal_yaw
                    res.pitch = cal_pitch
                    res.is_calibrating = (self.gaze_calibrator.state == "CALIBRATING")
                    res.calibration_progress = self.gaze_calibrator.calibration_progress
                    res.calibration_warning = self.gaze_calibrator.calibration_warning
                
            face_results = raw_results
            results["face"] = face_results
            
            # CHECK CALIBRATION COMPLETION
            if self.calibration_in_progress and self.gaze_calibrator.state == "CALIBRATED":
                logger.info("Calibration Successful. Starting Monitoring.")
                self.calibration_in_progress = False
                self.is_monitoring = True

            # Render Logic for Calibration
            # If we are strictly calibrating (and not yet switched to monitoring), return early
            if self.calibration_in_progress:
                vis_frame = self.visualizer.render(frame_data, [], face_results, None, None)
                # Pass results so UI can see "is_calibrating" flag
                return vis_frame, {"face": face_results}, None

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

            return vis_frame, results_map, risk_event
            

        return None, {}, None

    def start_calibration(self):
        """
        Triggers the calibration process.
        Detaches all other modules by setting is_monitoring = False.
        """
        logger.info("Starting Calibration Process... Detaching Modules.")
        
        # 1. Reset Flags
        self.is_monitoring = False
        self.calibration_in_progress = True
        
        # 2. Trigger Gaze Calibrator
        self.gaze_calibrator.start()

    def stop_calibration(self):
        """
        Manually cancels the calibration process.
        Resets everything to IDLE.
        """
        logger.info("Stopping Calibration Process (Manual or Failed).")
        self.calibration_in_progress = False
        self.is_monitoring = False
        
        # Reset Calibrator
        self.gaze_calibrator.stop()


