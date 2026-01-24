# 🛠️ Development Log (Devlog)

Here we track the technical evolution, challenges, and decisions made during the development of the Exam Proctoring System.

## 📅 Timeline

### [Current Date] - Initial Release & Tuning

#### **Phase 1: Architecture Design**

- **Decision**: Adopted a modular **Pipe and Filter** architecture.
- **Reasoning**: Decoupling detectors (MediaPipe/YOLO) from logic (Risk Engine) allows us to swap models easily without breaking the business logic.
- Defined `clean` interfaces: `IFaceDetector` and `IObjectDetector`.

#### **Phase 2: Core Implementation**

- Implemented threaded `Camera` capture for low-latency performance.
- Integrated **YOLOv8 Nano** for object detection (Phone/Person). It was chosen for its balance of speed and accuracy on CPU.

#### **Phase 3: The "MediaPipe/Protobuf" Conflict**

- **Issue**: `mediapipe` requires a specific protobuf version, while `tensorflow` (pulled by other libs) requires a newer one.
- **Error**: `AttributeError: module 'mediapipe' has no attribute 'solutions'`.
- **Solution**:
  1.  Migrated from legacy `mp.solutions` to the modern **MediaPipe Tasks API**.
  2.  Pinned `protobuf<5.0.0` in `requirements.txt`.
  3.  Implemented a `sys.modules` hack in `run.py` to prevent TensorFlow import collisions.

#### **Phase 4: The "OpenCV Unpacking" Bug**

- **Issue**: `ValueError: not enough values to unpack (expected 7, got 6)`.
- **Cause**: `cv2.RQDecomp3x3` returns different tuple lengths depending on the OpenCV version.
- **Fix**: Adjusted code to explicitly extract only the first element (Euler angles) from the return tuple.

#### **Phase 5: Sensitivity Tuning**

- **User Feedback**: "Looking away detection is too slow and insensitive."
- **Adjustments**:
  1.  **Yaw Threshold**: Lowered from `0.4` (~36°) to `0.22` (~20°) to detect smaller head turns.
  2.  **Temporal Filter**: Reduced `max_frames_looking_away` from `15` (0.5s) to `3` (0.1s) for "snappier" response.
  3.  **Risk Weight**: Increased Gaze weight from `0.4` to `0.5` to ensure it solidly triggers a MEDIUM risk event.

## 🔮 Future Roadmap

- [ ] **Audio Analysis**: Add microphone support to detect speaking/whispering.
- [ ] **Session Recording**: Save clips of high-risk events for review.
- [ ] **Web Dashboard**: Create a React/FastAPI frontend for remote proctoring.
- [ ] **Identity Verification**: Add initial face matching with ID card.
