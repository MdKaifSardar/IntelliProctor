import signal
import sys
import cv2
from app.infrastructure.logger import logger
from app.core.system_controller import SystemController

def signal_handler(sig, frame):
    logger.info("Signal received, shutting down...")
    sys.exit(0)

def main():
    # Setup Signal Handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize Controller
    controller = SystemController()
    controller.initialize()
    
    # Start Modules
    controller.start()
    
    logger.info("System Running. Press 'q' to exit.")

    try:
        while True:
            # Step returns the visualized frame
            vis_frame = controller.step()
            
            if vis_frame is not None:
                cv2.imshow("Proctoring System - Monitor", vis_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Shutting down...")
        controller.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
