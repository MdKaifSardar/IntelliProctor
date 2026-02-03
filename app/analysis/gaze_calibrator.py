from typing import Tuple, Optional
from app.config import settings

class GazeCalibrator:
    def __init__(self):
        # State
        self.state = "IDLE" # IDLE, CALIBRATING, CALIBRATED
        self.calibration_frames = 0
        self.calibration_target = settings.calibration.calibration_target_frames 
        
        # Baselines
        self.baseline_yaw = 0.0
        self.baseline_pitch = 0.0
        
        # Accumulators
        self._accum_yaw = 0.0
        self._accum_pitch = 0.0
        
        # Feedback
        self.calibration_warning = None
        self.calibration_progress = 0.0

    def start(self):
        """Start or Restart Calibration"""
        self.state = "CALIBRATING"
        self.reset_accumulators()
        self.calibration_warning = None
        self.calibration_progress = 0.0

    def stop(self):
        """Stop/Abort Calibration"""
        self.reset()

    def reset(self):
        """Reset to IDLE"""
        self.state = "IDLE"
        self.reset_accumulators()
        self.baseline_yaw = 0.0
        self.baseline_pitch = 0.0
        self.calibration_warning = None
        self.calibration_progress = 0.0

    def reset_accumulators(self):
        self.calibration_frames = 0
        self._accum_yaw = 0.0
        self._accum_pitch = 0.0

    def update(self, raw_yaw: float, raw_pitch: float) -> Tuple[float, float]:
        """
        Process a frame's raw gaze data.
        Returns: (calibrated_yaw, calibrated_pitch)
        """
        
        # If IDLE, just return raw offset by existing baseline (if any) or 0
        if self.state == "IDLE":
             return raw_yaw - self.baseline_yaw, raw_pitch - self.baseline_pitch

        # If CALIBRATED, apply baseline
        if self.state == "CALIBRATED":
             return raw_yaw - self.baseline_yaw, raw_pitch - self.baseline_pitch

        # If CALIBRATING
        if self.state == "CALIBRATING":
            # 1. Safety Check (Anti-Cheat)
            deg_yaw = abs(raw_yaw * 90)
            deg_pitch = abs(raw_pitch * 90)
            offset_limit = settings.calibration.MAX_CALIBRATION_OFFSET
            
            is_out_of_bounds = deg_yaw > offset_limit or deg_pitch > offset_limit
            
            if is_out_of_bounds:
                # PAUSE logic
                self.calibration_warning = "Look Straight to Continue!"
                # Do not accumulate
            else:
                self.calibration_warning = None
                self._accum_yaw += raw_yaw
                self._accum_pitch += raw_pitch
                self.calibration_frames += 1
                
                # Check Completion
                if self.calibration_frames >= self.calibration_target:
                    self.baseline_yaw = self._accum_yaw / self.calibration_target
                    self.baseline_pitch = self._accum_pitch / self.calibration_target
                    self.state = "CALIBRATED"
                    self.calibration_warning = None
            
            # Update Progress
            if self.calibration_target > 0:
                self.calibration_progress = min(1.0, self.calibration_frames / self.calibration_target)
            
            # During calibration, return 0.0 (perfect center) visually or raw?
            # User usually wants to see their movement. Let's return raw relative to 0 start.
            return raw_yaw, raw_pitch

        return raw_yaw, raw_pitch # Should not reach here
