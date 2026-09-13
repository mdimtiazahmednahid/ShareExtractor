from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QPushButton, QGroupBox, QLabel, QCheckBox)
from PySide6.QtCore import Signal
import datetime

class CollectorPanel(QGroupBox):
    start_requested = Signal()
    pause_requested = Signal()
    resume_requested = Signal()
    stop_requested = Signal()
    inspect_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Collector Controls", parent)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.lbl_status = QLabel("Status: IDLE")
        self.lbl_profiles = QLabel("Profiles: 0")
        self.lbl_scrolls = QLabel("Scrolls: 0")
        self.lbl_new = QLabel("New this pass: 0")
        
        for lbl in (self.lbl_status, self.lbl_profiles, self.lbl_scrolls, self.lbl_new):
            stats_layout.addWidget(lbl)
            
        # Settings
        settings_layout = QHBoxLayout()
        self.chk_auto_retry = QCheckBox("Auto-Retry on scroll stop (5s)")
        self.chk_auto_retry.setChecked(True)
        self.chk_auto_save = QCheckBox("Auto-Export CSV")
        self.chk_auto_save.setChecked(True)
        settings_layout.addWidget(self.chk_auto_retry)
        settings_layout.addWidget(self.chk_auto_save)
        settings_layout.addStretch()
            
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_inspect = QPushButton("Inspect UI")
        self.btn_inspect.clicked.connect(self.inspect_requested.emit)
        
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_requested.emit)
        self.btn_start.setEnabled(False) # Needs connection first
        
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_requested.emit)
        self.btn_pause.setEnabled(False)
        
        self.btn_resume = QPushButton("Resume")
        self.btn_resume.clicked.connect(self.resume_requested.emit)
        self.btn_resume.setEnabled(False)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_requested.emit)
        self.btn_stop.setEnabled(False)
        
        btn_layout.addWidget(self.btn_inspect)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_resume)
        btn_layout.addWidget(self.btn_stop)
        
        self.layout.addLayout(stats_layout)
        self.layout.addLayout(settings_layout)
        self.layout.addLayout(btn_layout)

    def update_status(self, status: str):
        self.lbl_status.setText(f"Status: {status}")
        
        # State machine for buttons
        if status == "COLLECTING":
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.btn_inspect.setEnabled(False)
        elif status == "PAUSED":
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.btn_inspect.setEnabled(True)
        elif status in ("COMPLETED", "IDLE"):
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.btn_inspect.setEnabled(True)

    def update_stats(self, total_profiles, total_scrolls, new_this_pass):
        self.lbl_profiles.setText(f"Profiles: {total_profiles}")
        self.lbl_scrolls.setText(f"Scrolls: {total_scrolls}")
        self.lbl_new.setText(f"New this pass: {new_this_pass}")
