import cv2
import time
import signal
import sys
from app.config import settings
from app.infrastructure.logger import logger
from app.infrastructure.camera import Camera
from app.infrastructure.visualizer import Visualizer
from app.detectors.face_detector import FaceDetector
from app.detectors.object_detector import ObjectDetector
from app.analysis.behavior import BehaviorAnalyzer
from app.analysis.risk_engine import RiskEngine

def signal_handler(sig, frame):
    logger.info("Signal received, shutting down...")
    sys.exit(0)

def main():
    # Setup Signal Handler
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Initializing Proctoring System...")
    
    # 1. Initialize Components
    try:
        camera = Camera()
        face_detector = FaceDetector()
        object_detector = ObjectDetector()
        behavior_analyzer = BehaviorAnalyzer()
        risk_engine = RiskEngine()
        visualizer = Visualizer()
    except Exception as e:
        logger.critical(f"Failed to initialize components: {e}")
        return

    # 2. Start Camera
    try:
        camera.start()
    except RuntimeError:
        logger.critical("Camera failed to start.")
        return

    logger.info("System Running. Press 'q' to exit.")

    try:
        while True:
            # 3. Capture
            frame_data = camera.read()
            if frame_data is None:
                time.sleep(0.01)
                continue
            
            # 4. Detect
            # Run in serial for simplicity, could be parallelized
            face_results = face_detector.process(frame_data)
            object_results = object_detector.detect(frame_data)
            
            # 5. Analyze
            signals = behavior_analyzer.analyze(
                timestamp=frame_data.timestamp,
                face_results=face_results,
                object_results=object_results
            )
            
            # 6. Risk Scoring
            risk_event = risk_engine.process(signals)
            if risk_event:
                logger.warning(f"RISK EVENT: {risk_event.risk_level} - {risk_event.reasons}")
                
            # 7. Visualize
            vis_frame = visualizer.render(
                frame_data, 
                object_results, 
                face_results, 
                risk_event
            )
            
            # 8. Display
            cv2.imshow("Proctoring System - Monitor", vis_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Shutting down...")
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
