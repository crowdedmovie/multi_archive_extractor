# Stylesheet definitions for dark and light themes.

DARK_THEME_STYLESHEET = """
    QProgressBar {
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        text-align: center;
        background-color: #1a1a1a;
    }
    QProgressBar::chunk {
        background-color: #2a82da;
        border-radius: 3px;
    }
    QTextEdit {
        background-color: #1a1a1a;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        padding: 3px;
        color: #d2d2d2;
    }
    QMainWindow {
        background-color: #2d2d2d;
    }
    QWidget {
        background-color: #2d2d2d;
        color: #d2d2d2;
    }
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #4a4a4a;
        border-radius: 4px;
        padding: 5px 15px;
        color: #e0e0e0;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
        color: #ffffff;
    }
    QPushButton:pressed {
        background-color: #2a2a2a;
        color: #ffffff;
    }
    QPushButton:disabled {
        background-color: #2d2d2d;
        color: #7f7f7f;
        border: 1px solid #3a3a3a;
    }
    QLineEdit {
        background-color: #1a1a1a;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        padding: 3px;
        color: #d2d2d2;
    }
    QLabel {
        color: #d2d2d2;
    }
    QCheckBox {
        color: #d2d2d2;
    }
    QCheckBox::indicator {
        width: 15px;
        height: 15px;
        border: 1px solid #3a3a3a;
        border-radius: 3px;
        background-color: #1a1a1a;
    }
    QCheckBox::indicator:checked {
        background-color: #2a82da;
    }
    QGroupBox {
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }
    QGroupBox::title {
        color: #d2d2d2;
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
    }
    QMenuBar {
        background-color: #2d2d2d;
        color: #d2d2d2;
    }
    QMenuBar::item:selected {
        background-color: #353535;
    }
    QMenu {
        background-color: #2d2d2d;
        color: #d2d2d2;
        border: 1px solid #3a3a3a;
    }
    QMenu::item:selected {
        background-color: #353535;
    }
    #btnSelectSource, #btnSelectDestination {
        background-color: #2a82da;  /* Bright blue */
        color: #ffffff;
        border: 1px solid #3a9de3;
    }
    #btnSelectSource:hover, #btnSelectDestination:hover {
        background-color: #3a9de3;
    }
    #btnSelectSource:pressed, #btnSelectDestination:pressed {
        background-color: #1a72ca;
    }
"""

LIGHT_THEME_STYLESHEET = """
    QProgressBar {
        border: 1px solid #c8c8c8;
        border-radius: 4px;
        text-align: center;
        background-color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 3px;
    }
    QTextEdit {
        background-color: #ffffff;
        border: 1px solid #c8c8c8;
        border-radius: 4px;
        padding: 3px;
        color: #000000;
    }
    QMainWindow {
        background-color: #ffffff;
    }
    QWidget {
        background-color: #ffffff;
        color: #000000;
    }
    QPushButton {
        background-color: #f0f0f0;
        border: 1px solid #c8c8c8;
        border-radius: 4px;
        padding: 5px 15px;
        color: #000000;
    }
    QPushButton:hover {
        background-color: #e0e0e0;
    }
    QPushButton:pressed {
        background-color: #d0d0d0;
    }
    QPushButton:disabled {
        background-color: #f0f0f0;
        color: #7f7f7f;
        border: 1px solid #c8c8c8;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #c8c8c8;
        border-radius: 4px;
        padding: 3px;
        color: #000000;
    }
    QLabel {
        color: #000000;
    }
    QCheckBox {
        color: #000000;
    }
    QCheckBox::indicator {
        width: 15px;
        height: 15px;
        border: 1px solid #c8c8c8;
        border-radius: 3px;
        background-color: #ffffff;
    }
    QCheckBox::indicator:checked {
        background-color: #0078d4;
    }
    QGroupBox {
        border: 1px solid #c8c8c8;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }
    QGroupBox::title {
        color: #000000;
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
    }
    QMenuBar {
        background-color: #ffffff;
        color: #000000;
    }
    QMenuBar::item:selected {
        background-color: #f0f0f0;
    }
    QMenu {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #c8c8c8;
    }
    QMenu::item:selected {
        background-color: #f0f0f0;
    }
"""
