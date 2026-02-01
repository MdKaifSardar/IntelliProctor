import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple
from app.core.interfaces import IFaceDetector
from app.core.schemas import FrameData, FaceResult
from app.config import settings

# Import Tasks API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FaceDetector(IFaceDetector):
    def __init__(self):
        # Calibration State
        self.state = "IDLE" # IDLE, CALIBRATING, CALIBRATED
        self.calibration_frames = 0
        self.calibration_target = 60 # ~2 seconds
        self.baseline_yaw = 0.0
        self.baseline_pitch = 0.0
        self.baseline_roll = 0.0
        self.is_calibrating = False 
        self.calibration_warning = None
        
        # Safety Limits (Max deviation from Absolute Zero in degrees)
        self.MAX_CALIBRATION_OFFSET = 20.0 
        
        # Create FaceLandmarker options
        base_options = python.BaseOptions(model_asset_path='app/models/face_landmarker.task')
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False, # Can be true for easier pose!
            num_faces=1,
            min_face_detection_confidence=settings.face.min_detection_confidence,
            min_face_presence_confidence=settings.face.min_tracking_confidence,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def warmup(self):
        """Runs a dummy inference to load model weights (Fixes startup lag)"""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=dummy_frame)
        self.detector.detect(mp_image)

    def start_calibration(self):
        """Triggers manual calibration sequence"""
        self.state = "CALIBRATING"
        self.calibration_frames = 0
        self.baseline_yaw = 0.0
        self.baseline_pitch = 0.0
        self.baseline_roll = 0.0
        
        # Accumulators (Separate from baseline to avoid visual drift during cal)
        self._accum_yaw = 0.0
        self._accum_pitch = 0.0
        
        self.calibration_warning = None
        self.is_calibrating = True
        
    def _calculate_head_pose(self, landmarks, image_shape) -> Tuple[float, float]:
        """
        Estimate head pose (yaw, pitch) from landmarks.
        Returns angles in radians (approximate).
        """
        img_h, img_w, _ = image_shape
        face_3d = []
        face_2d = []

        # Specific landmarks for head pose estimation
        # Nose tip: 1, Chin: 152, Left eye left corner: 33, Right eye right corner: 263, Left Mouth: 61, Right Mouth: 291
        landmark_indices = [33, 263, 1, 61, 291, 199]
        
        # Generic 3D Face Model (X, Y, Z)
        # Corresponding to indices: [33, 263, 1, 61, 291, 199]
        # (Left Eye, Right Eye, Nose, Left Mouth, Right Mouth, Chin)
        # Coordinates in arbitrary units, centered at Nose tip (0,0,0)
        # Y-axis points DOWN (matching image coords)
        # Generic 3D Face Model (X, Y, Z)
        # Corresponding to indices: [33, 263, 1, 61, 291, 199]
        # (Left Eye, Right Eye, Nose, Left Mouth, Right Mouth, Chin)
        # Coordinates in arbitrary units, centered at Nose tip (0,0,0)
        # Y-axis points DOWN (matching image coords)
        # Z-axis points INTO screen (Standard OpenCV): Nose=0, Eyes=Positive (Further)
        face_3d = np.array([
            [-225.0, -170.0,  135.0], # 33: Left Eye
            [ 225.0, -170.0,  135.0], # 263: Right Eye
            [   0.0,    0.0,    0.0], # 1: Nose
            [-150.0,  150.0,  125.0], # 61: Left Mouth
            [ 150.0,  150.0,  125.0], # 291: Right Mouth
            [   0.0,  330.0,   65.0]  # 199: Chin
        ], dtype=np.float64)

        for idx in landmark_indices:
            lm = landmarks[idx]
            x, y = int(lm.x * img_w), int(lm.y * img_h)
            face_2d.append([x, y])
            # face_3d is now static, no appending needed
            
        face_2d = np.array(face_2d, dtype=np.float64)

        # Camera matrix
        focal_length = 1 * img_w
        cam_matrix = np.array([
            [focal_length, 0, img_h / 2],
            [0, focal_length, img_w / 2],
            [0, 0, 1]
        ])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        # Solve PnP
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        
        if not success:
            return 0.0, 0.0

        # Get rotational matrix
        rmat, jac = cv2.Rodrigues(rot_vec)

        # Get angles
        pose_data = cv2.RQDecomp3x3(rmat)
        angles = pose_data[0]
        
        # Angles in degrees (RQDecomp3x3 returns degrees)
        pitch = angles[0]
        yaw = angles[1]
        # roll = angles[2] # Unused
        
        # DEBUG: Print raw angles to terminal to diagnose offset
        # print(f"DEBUG RAW -> Pitch: {pitch:.2f}, Yaw: {yaw:.2f}, Roll: {roll:.2f}")
        
        return yaw / 90.0, pitch / 90.0

    def process(self, frame_data: FrameData) -> List[FaceResult]:
        image = frame_data.frame
        # MediaPipe Tasks requires mp.Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        detection_result = self.detector.detect(mp_image)
        
        if not detection_result.face_landmarks:
            # If we lose face during calibration, abort? 
            # For now just return empty, calibration will effectively pause or continue next frame
            return [FaceResult(face_present=False, is_calibrating=self.is_calibrating)]
        
        face_results = []
        for face_landmarks in detection_result.face_landmarks:
            # Raw values (Normalized -1.0 to 1.0)
            raw_yaw, raw_pitch = self._calculate_head_pose(face_landmarks, image.shape)
            
            # State Machine
            if self.state == "CALIBRATING":
                # 1. Safety Check (Anti-Cheat)
                # Convert normalized angles back to degrees approx (x90) for intuitive check
                deg_yaw = abs(raw_yaw * 90)
                deg_pitch = abs(raw_pitch * 90)
                
                is_out_of_bounds = deg_yaw > self.MAX_CALIBRATION_OFFSET or deg_pitch > self.MAX_CALIBRATION_OFFSET
                
                # GRACE PERIOD: First 10 frames (approx 0.5s), we allow out-of-bounds.
                if is_out_of_bounds:
                    if self.calibration_frames < 10:
                         self.calibration_warning = "Aligning..."
                         pass
                    else:
                        # NEW LOGIC: PAUSE, DON'T ABORT
                        self.calibration_warning = "Look Straight to Continue!"
                        # Do NOT increment self.calibration_frames
                        # Do NOT update self.state
                else:
                    # 2. Accumulate
                    self._accum_yaw += raw_yaw
                    self._accum_pitch += raw_pitch
                    # self._accum_roll += raw_roll # Unused
                    self.calibration_frames += 1
                    self.calibration_warning = f"Calibrating... {int((self.calibration_frames/self.calibration_target)*100)}%"
                    
                    # 3. Finalize
                    if self.calibration_frames >= self.calibration_target:
                        self.baseline_yaw = self._accum_yaw / self.calibration_target
                        self.baseline_pitch = self._accum_pitch / self.calibration_target
                        self.baseline_roll = 0.0 # Unused
                        self.state = "CALIBRATED"
                        self.is_calibrating = False
                        self.calibration_warning = None # Success
            
            # Apply Calibration (if any baseline exists)
            yaw = raw_yaw - self.baseline_yaw
            pitch = raw_pitch - self.baseline_pitch
            roll = 0.0 # Unused
            
            face_results.append(FaceResult(
                face_present=True,
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                landmarks=face_landmarks,
                is_calibrating=self.is_calibrating,
                calibration_warning=self.calibration_warning
            ))
            
        return face_results
