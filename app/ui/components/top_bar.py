from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QWidget
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon

class TopBar(QFrame):
    toggle_sidebar_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(60)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # Menu Button
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon("app/assets/menu.svg"))
        self.btn_menu.setIconSize(QSize(24, 24))
        self.btn_menu.setFixedSize(40, 40)
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.setObjectName("MenuButton") # Transparent style
        self.btn_menu.clicked.connect(self.toggle_sidebar_signal.emit)
        layout.addWidget(self.btn_menu)
        
        layout.addSpacing(15)
        
        # Title
        title = QLabel("Proctoring Session")
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # User Profile (Mock)
        user_label = QLabel("Student: John Doe (ID: 12345)")
        user_label.setObjectName("HeaderUser")
        layout.addWidget(user_label)
