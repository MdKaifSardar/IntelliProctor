# Intelligent Exam Proctoring System

A modular, computer-vision-based **decision support system** designed to assist proctors by detecting potential risk indicators in real-time. This system analyzes webcam feeds to flag suspicious behaviors such as device usage, multiple people, and extensive gaze aversion.

> **⚠️ Disclaimer**: This system is designed to **assist** human proctors, not replace them. It flags potential risks for review. It does not make definitive judgments on cheating.

## 🚀 Features

- **Real-time Analysis**: Processes webcam feed at ~30 FPS.
- **Face & Gaze Tracking**: Detects facial presence and head pose (yaw/pitch) to identify looking-away behaviors.
  - **Auto-Calibration**: Zeroes out head pose on startup for accurate relative tracking.
- **Audio Detection**: Monitors microphone for high volume or speech patterns.
- **Object Detection**: Identifies potential malpractice objects:
  - 📱 Mobile Phones
  - 👥 Multiple People
  - 🎧 Headphones (Experimental)
- **Risk Engine**:
  - Aggregates temporal signals (ignores momentary glitches).
  - Flags `PITCH` (Looking Up/Down) and `AUDIO` violations.
  - Calculates a generic Risk Score.
  - Triggers `LOW`, `MEDIUM`, or `HIGH` risk events with explainable reasons.
- **Visual Overlay**: Provides immediate visual feedback (bounding boxes, status text) and risk alerts.
- **Proctor Sidebar**:
  - **Event Log**: A scrollable history of all risk events and system statuses.
  - **Calibration Progress**: Visual bar showing synchronization status.
  - **Real-time Telemetry**: Live view of Head Pose (Yaw/Pitch) and Audio Levels.
- **Privacy-First**: Does not store video feeds or identify individuals (no facial recognition, only detection).

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **GUI Framework**: PyQt6 (Desktop Application)
- **Computer Vision**:
  - **MediaPipe Tasks**: Robust Face Landmark detection.
  - **OpenCV**: Image processing and visualization.
  - **YOLOv8** (Ultralytics): Fast and accurate object detection.
- **Architecture**: Modular "Pipe & Filter" design (Camera -> Detectors -> Analysis -> Risk -> UI).
- **Configuration**: Pydantic-based settings management.

## 📦 Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd cheat-detection
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    _Note: This will automatically handle the specific `protobuf` and `mediapipe` version requirements._

## ▶️ Usage

1.  **Run the Application**:

    ```bash
    python run.py
    ```

    _First run will download necessary models (`yolov8n.pt`, `face_landmarker.task`)._

2.  **Controls**:
    - Press **`q`** to exit the application.

3.  **Understanding the UI**:
    - **Green/Blue Boxes**: Detected objects (Person, Phone).
    - **Yellow Text**: Real-time status (e.g., `Head: Side Looking`).
    - **Top Header**: Current Risk Level.
      - **Red**: High Risk (e.g., Phone detected).
      - **Yellow**: Medium Risk (e.g., Extensive looking away).

## 📂 Project Structure

```
app/
├── analysis/           # Logic & State
│   ├── behavior.py     # Temporal aggregation (rolling windows)
│   └── risk_engine.py  # Scoring logic
├── core/               # Shared logic
│   ├── interfaces.py   # Abstract base classes
│   └── schemas.py      # Data structures (Pydantic)
├── detectors/          # CV Models
│   ├── face_detector.py   # MediaPipe implementation
│   └── object_detector.py # YOLO implementation
├── infrastructure/     # I/O
│   ├── camera.py       # Threaded capture
│   └── visualizer.py   # Drawing utils
├── models/             # Model weights storage
├── config.py           # Configuration settings
└── main.py             # Application orchestrator
run.py                  # Entry point
requirements.txt        # Dependencies
DEVLOG.md               # Development history & notes
```

## ⚙️ Configuration

You can tune sensitivity in `app/config.py`:

- **Active Modules**: Enable/disable `face`, `audio`, `object` modules dynamically.
- **Risk Thresholds**: Adjust `weight_phone`, `weight_gaze`, `audio.threshold_rms`, etc.
- **Timing**: Adjust `max_frames_looking_away` (lower = faster detection).
- **Visualization**: Toggle `visualize_landmarks` for debug dots.

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch.
3.  Commit your changes.
4.  Open a Pull Request.

## 📄 License

[MIT License](LICENSE)
