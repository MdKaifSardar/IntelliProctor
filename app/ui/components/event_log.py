from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtCore import Qt, QSize
from datetime import datetime
from app.core.schemas import RiskEvent, RiskLevel

class LogCard(QFrame):
    def __init__(self, title, message, color_code, time_str, icon_path=None):
        super().__init__()
        self.setObjectName("LogCard")
        # Inline styling for now (or move to global)
        self.setStyleSheet(f"""
            QFrame#LogCard {{
                background-color: {color_code}20; /* 20 = 12% opacity */
                border-left: 4px solid {color_code};
                border-radius: 4px;
                margin-bottom: 5px;
            }}
            QLabel {{ background-color: transparent; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        # Header (Time + Title)
        header_layout = QVBoxLayout() # Simplification
        
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(lbl_time)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {color_code}; font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_title)
        
        if message:
            lbl_msg = QLabel(message)
            lbl_msg.setWordWrap(True)
            lbl_msg.setStyleSheet("color: #cccccc; font-size: 12px;")
            layout.addWidget(lbl_msg)

class EventLog(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel("Session Log")
        lbl.setStyleSheet("font-weight: bold; color: #888888; margin-bottom: 5px;")
        self.layout.addWidget(lbl)
        
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("EventLogList")
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QListWidget::item { margin-bottom: 5px; }
            QListWidget::item:hover { background-color: transparent; }
            QListWidget::item:selected { background-color: transparent; }
        """)
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.layout.addWidget(self.list_widget)

    def _add_entry(self, title, message, color):
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # Create Widget
        card = LogCard(title, message, color, time_str)
        
        # Create Item
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(card.sizeHint()) # Initial hint
        
        # Add to list
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, card)
        self.list_widget.scrollToBottom()

    def log_message(self, message: str, color: str = "white"):
        # Map color names to Hex
        hex_map = {
            "white": "#ffffff",
            "red": "#ff4444",
            "orange": "#ffbb33",
            "green": "#00C851",
            "blue": "#33b5e5"
        }
        hex_color = hex_map.get(color, color)
        if not hex_color.startswith("#"): hex_color = "#ffffff"
        
        self._add_entry("System", message, hex_color)

    def log_risk_event(self, event: RiskEvent):
        color = "#ff4444" # High
        if event.risk_level == RiskLevel.MEDIUM: color = "#ffbb33"
        if event.risk_level == RiskLevel.LOW: color = "#00C851"
        
        reasons_text = ", ".join(event.reasons)
        self._add_entry(f"Risk: {event.risk_level.value}", reasons_text, color)

    def reset(self):
        self.list_widget.clear()
