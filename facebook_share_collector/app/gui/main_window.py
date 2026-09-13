import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter, 
                               QTabWidget, QMessageBox)
from PySide6.QtCore import Qt

from app.gui.device_panel import DevicePanel
from app.gui.collector_panel import CollectorPanel
from app.gui.results_panel import ResultsPanel
from app.gui.logs_panel import LogsPanel
from app.automation.appium_manager import AppiumManager
from app.automation.collector_engine import CollectorEngine
from app.automation.ui_inspector import UIInspector
from app.models.collection_session import CollectionSession
from app.database.repository import DatabaseRepository
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facebook Share Collector")
        self.resize(1000, 700)
        
        self.settings = get_settings()
        self.appium_manager = AppiumManager(
            host=self.settings.get('appium.host', '127.0.0.1'),
            port=self.settings.get('appium.port', 4723)
        )
        self.db = DatabaseRepository()
        self.engine = None
        self.current_session = None

        self._setup_ui()

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Top controls
        self.device_panel = DevicePanel(self.appium_manager)
        self.device_panel.device_connected.connect(self._on_device_connected)
        
        self.collector_panel = CollectorPanel()
        self.collector_panel.start_requested.connect(self._start_collection)
        self.collector_panel.pause_requested.connect(self._pause_collection)
        self.collector_panel.resume_requested.connect(self._resume_collection)
        self.collector_panel.stop_requested.connect(self._stop_collection)
        self.collector_panel.inspect_requested.connect(self._inspect_ui)
        
        layout.addWidget(self.device_panel)
        layout.addWidget(self.collector_panel)
        
        # Bottom split view (Results / Logs)
        splitter = QSplitter(Qt.Vertical)
        
        self.results_panel = ResultsPanel()
        self.logs_panel = LogsPanel()
        
        tabs = QTabWidget()
        tabs.addTab(self.results_panel, "Results")
        
        splitter.addWidget(tabs)
        splitter.addWidget(self.logs_panel)
        splitter.setSizes([400, 200])
        
        layout.addWidget(splitter, 1)

    def _on_device_connected(self, serial):
        self.collector_panel.btn_start.setEnabled(True)
        self.collector_panel.btn_inspect.setEnabled(True)

    def _inspect_ui(self):
        driver = self.appium_manager.get_driver()
        if not driver:
            QMessageBox.warning(self, "Warning", "Appium is not connected.")
            return
            
        xml_source = UIInspector.get_page_source(driver)
        if xml_source:
            xml_path, json_path = UIInspector.save_inspection(xml_source)
            logger.info(f"UI Inspection saved to {xml_path}")
            QMessageBox.information(self, "Inspection Complete", f"Saved UI hierarchy to:\n{xml_path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to retrieve page source.")

    def _start_collection(self):
        self.current_session = CollectionSession()
        self.db.create_session(self.current_session)
        
        self.engine = CollectorEngine(self.appium_manager, self.current_session, self.settings._config)
        self.engine.status_updated.connect(self.collector_panel.update_status)
        self.engine.stats_updated.connect(self.collector_panel.update_stats)
        self.engine.profile_found.connect(self._on_profile_found)
        self.engine.finished_collection.connect(self._on_collection_finished)
        self.engine.error_occurred.connect(self._on_error)
        
        self.engine.start()
        
    def _pause_collection(self):
        if self.engine:
            self.engine.pause()
            
    def _resume_collection(self):
        if self.engine:
            self.engine.resume()
            
    def _stop_collection(self):
        if self.engine:
            self.engine.stop()

    def _on_profile_found(self, profile):
        self.db.save_profile(profile)
        self.results_panel.add_profile(profile)

    def _on_collection_finished(self):
        if self.current_session:
            import datetime
            self.current_session.end_time = datetime.datetime.now().isoformat()
            self.current_session.status = "COMPLETED"
            self.db.update_session(self.current_session)
            logger.info(f"Session {self.current_session.id} completed. Total profiles: {self.current_session.total_profiles}")

    def _on_error(self, message):
        QMessageBox.critical(self, "Error", message)
        
    def closeEvent(self, event):
        if self.engine and self.engine.isRunning():
            self.engine.stop()
            self.engine.wait()
        self.appium_manager.disconnect()
        super().closeEvent(event)
