from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

class VideoFeed(QLabel):
    def __init__(self):
        super().__init__("Waiting for Camera...")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        self.setMinimumSize(640, 480) # 4:3 Aspect Ratio base
        self.setScaledContents(False) # We handle scaling manually for aspect ratio

    def update_frame(self, qt_image: QImage):
        """Slot to receive new frame from worker"""
        # Scale to fit label while keeping aspect ratio
        if qt_image.isNull():
            return
            
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

    def reset(self):
        self.setText("Waiting for Camera...")
