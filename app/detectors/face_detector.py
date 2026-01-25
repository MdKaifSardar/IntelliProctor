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
        
    def _calculate_head_pose(self, landmarks, image_shape) -> Tuple[float, float, float]:
        """
        Estimate head pose (yaw, pitch, roll) from landmarks.
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
        face_3d = np.array([
            [-225.0, -170.0, -135.0], # 33: Left Eye
            [ 225.0, -170.0, -135.0], # 263: Right Eye
            [   0.0,    0.0,    0.0], # 1: Nose
            [-150.0,  150.0, -125.0], # 61: Left Mouth
            [ 150.0,  150.0, -125.0], # 291: Right Mouth
            [   0.0,  330.0,  -65.0]  # 199: Chin
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
            return 0.0, 0.0, 0.0

        # Get rotational matrix
        rmat, jac = cv2.Rodrigues(rot_vec)

        # Get angles
        pose_data = cv2.RQDecomp3x3(rmat)
        angles = pose_data[0]
        
        # Angles in degrees (RQDecomp3x3 returns degrees)
        pitch = angles[0]
        yaw = angles[1]
        roll = angles[2]
        
        return yaw / 90.0, pitch / 90.0, roll / 90.0

    def process(self, frame_data: FrameData) -> List[FaceResult]:
        image = frame_data.frame
        # MediaPipe Tasks requires mp.Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        detection_result = self.detector.detect(mp_image)
        
        if not detection_result.face_landmarks:
            return [FaceResult(face_present=False)]
        
        face_results = []
        for face_landmarks in detection_result.face_landmarks:
            # face_landmarks is a list of NormalizedLandmark
            yaw, pitch, roll = self._calculate_head_pose(face_landmarks, image.shape)
            
            face_results.append(FaceResult(
                face_present=True,
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                landmarks=face_landmarks # Pass raw landmarks for visualization
            ))
            
        return face_results
