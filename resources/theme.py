DARK_THEME_QSS = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}
QLineEdit, QPlainTextEdit {
    background-color: #3c3f41;
    color: #ffffff;
    border: 1px solid #555;
}
QPushButton {
    background-color: #555555;
    border: 1px solid #444;
}
QPushButton:hover {
    background-color: #666666;
}
QCheckBox, QLabel {
    font-size: 14px;
}
QComboBox {
    background-color: #3c3f41;
    color: #ffffff;
}
"""


def apply_theme(widget, theme_choice: str):
    """
    Switch between Light, Dark, or System theme. The widget is typically the QApplication or QMainWindow.
    """
    if theme_choice.lower() == "dark":
        widget.setStyleSheet(DARK_THEME_QSS)
    else:
        # 'Light' or 'System' => clear style
        widget.setStyleSheet("")
