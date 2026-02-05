
# Modern Dark/Blue Theme (VS Code / Linear inspired)

# Color Palette
# Backgrounds: #1e1e1e (Main), #252526 (Sidebar), #333333 (Input)
# Accents: #007acc (Blue), #0e639c (Blue Hover)
# Text: #d4d4d4 (Main), #cccccc (Secondary)
# Status: #28a745 (Green), #dc3545 (Red), #ffc107 (Yellow)

GLOBAL_STYLES = """
QMainWindow {
    background-color: #252526; /* Slightly lighter than #1e1e1e */
    color: #d4d4d4;
    font-family: "Segoe UI", "Roboto", "Arial";
    font-size: 14px;
}

QWidget {
    font-family: "Segoe UI", "Roboto", "Arial";
    color: #d4d4d4;
    /* Don't set background-color here globally, or transparent widgets break */
}

/* --- SIDEBAR --- */
QFrame#Sidebar {
    background-color: #2d2d30; /* Lighter compared to main */
    border-left: 1px solid #3e3e42;
}

QLabel#SidebarTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    padding: 10px;
}

/* --- CARDS (Status, Telemetry, Log) --- */
QFrame.Card {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 6px;
    padding: 5px;
}

/* --- BUTTONS --- */
QPushButton {
    background-color: #0078d4; /* Windows 11 Blue */
    color: white;
    border: 1px solid #00000000;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #0e639c;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #3a3d41;
    color: #858585;
}

QPushButton#StopButton {
    background-color: #d83b01;
}

QPushButton#StopButton:hover {
    background-color: #c50f1f;
}

/* --- PROGRESS BAR --- */
QProgressBar {
    border: 1px solid #3e3e42;
    border-radius: 4px;
    background-color: #2d2d30;
    text-align: center;
    color: white;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #28a745;
    border-radius: 3px;
}

/* --- STATUS INDICATOR --- */
QLabel#StatusLabel {
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
    color: #1e1e1e; /* Text is usually black on colored status pills */
}

/* --- LOG --- */
QTextEdit#EventLog {
    background-color: #1e1e1e;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: #264f78;
}
"""
