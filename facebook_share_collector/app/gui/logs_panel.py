from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt
import logging

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)
        # Monospace font
        font = self.widget.font()
        font.setFamily("Courier")
        self.widget.setFont(font)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class LogsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.log_handler = QTextEditLogger(self)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt="%H:%M:%S")
        self.log_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(self.log_handler)
        
        self.layout.addWidget(self.log_handler.widget)
        
    def append_log(self, text):
        self.log_handler.widget.append(text)
