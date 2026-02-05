import sys
# Hack: Disable tensorflow import to prevent protobuf conflict with MediaPipe
sys.modules["tensorflow"] = None
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.infrastructure.logger import logger

def main():
    logger.info("Starting Proctoring Desktop App...")
    
    app = QApplication(sys.argv)
    
    # Apply Global Styles (Theme)
    from app.ui.styles import GLOBAL_STYLES
    app.setStyleSheet(GLOBAL_STYLES)
    
    window = MainWindow()
    window.show()
    
    exit_code = app.exec()
    logger.info(f"Application exited with code {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
