from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QComboBox, QPushButton, QGroupBox, QLineEdit, QMessageBox)
from PySide6.QtCore import Signal
from app.automation.device_manager import DeviceManager
from app.automation.appium_manager import AppiumManager

class DevicePanel(QGroupBox):
    # Signal emitted when a device is connected successfully
    device_connected = Signal(str) 

    def __init__(self, appium_manager: AppiumManager, parent=None):
        super().__init__("Device & Connection Status", parent)
        self.appium_manager = appium_manager
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # ADB Devices
        adb_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh Devices")
        self.refresh_btn.clicked.connect(self.refresh_devices)
        
        adb_layout.addWidget(QLabel("Device:"))
        adb_layout.addWidget(self.device_combo, 1)
        adb_layout.addWidget(self.refresh_btn)
        
        # Connect to Appium
        conn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect Appium")
        self.connect_btn.clicked.connect(self.connect_appium)
        self.status_label = QLabel("Appium: DISCONNECTED")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.status_label)
        conn_layout.addStretch()
        
        # URL Launcher
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.facebook.com/share/...")
        self.open_url_btn = QPushButton("Open URL on Phone")
        self.open_url_btn.clicked.connect(self.open_url)
        
        url_layout.addWidget(QLabel("Launch URL:"))
        url_layout.addWidget(self.url_input, 1)
        url_layout.addWidget(self.open_url_btn)
        
        self.layout.addLayout(adb_layout)
        self.layout.addLayout(url_layout)
        self.layout.addLayout(conn_layout)
        
        self.refresh_devices()

    def refresh_devices(self):
        self.device_combo.clear()
        devices = DeviceManager.get_connected_devices()
        for dev in devices:
            if dev['state'] == 'device':
                self.device_combo.addItem(f"{dev['model']} ({dev['serial']})", dev['serial'])
                
        if self.device_combo.count() == 0:
            self.device_combo.addItem("No devices found", None)

    def connect_appium(self):
        serial = self.device_combo.currentData()
        if not serial:
            return
            
        self.status_label.setText("Appium: CONNECTING...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        if self.appium_manager.connect(serial):
            self.status_label.setText("Appium: CONNECTED")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.device_connected.emit(serial)
            self.connect_btn.setEnabled(False)
        else:
            self.status_label.setText("Appium: ERROR")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def open_url(self):
        serial = self.device_combo.currentData()
        url = self.url_input.text().strip()
        
        if not serial:
            QMessageBox.warning(self, "Warning", "Please select a connected device first.")
            return
            
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a valid URL.")
            return
            
        success = DeviceManager.open_url(serial, url)
        if success:
            QMessageBox.information(self, "Success", "URL launched on the device!")
        else:
            QMessageBox.critical(self, "Error", "Failed to open URL. Is the device connected and unlocked?")
