from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from app.models.share_profile import ShareProfile
from app.exporters.csv_exporter import CSVExporter
from app.exporters.json_exporter import JSONExporter
from app.exporters.xlsx_exporter import XLSXExporter
import datetime
import os

class ResultsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profiles = []
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Profile URL", "Share URL", "Confidence", "First Seen"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Export Buttons
        btn_layout = QHBoxLayout()
        self.btn_csv = QPushButton("Export CSV")
        self.btn_csv.clicked.connect(self.export_csv)
        self.btn_json = QPushButton("Export JSON")
        self.btn_json.clicked.connect(self.export_json)
        self.btn_xlsx = QPushButton("Export XLSX")
        self.btn_xlsx.clicked.connect(self.export_xlsx)
        self.btn_clear = QPushButton("Clear Results")
        self.btn_clear.clicked.connect(self.clear_results)
        
        btn_layout.addWidget(self.btn_csv)
        btn_layout.addWidget(self.btn_json)
        btn_layout.addWidget(self.btn_xlsx)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_clear)
        
        self.layout.addWidget(self.table)
        self.layout.addLayout(btn_layout)

    def add_profile(self, profile: ShareProfile):
        self.profiles.append(profile)
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.table.setItem(row, 0, QTableWidgetItem(profile.name))
        self.table.setItem(row, 1, QTableWidgetItem(profile.profile_url or ""))
        self.table.setItem(row, 2, QTableWidgetItem(profile.share_url or ""))
        self.table.setItem(row, 3, QTableWidgetItem(f"{profile.confidence:.2f}"))
        self.table.setItem(row, 4, QTableWidgetItem(profile.first_seen_at.split('.')[0].replace('T', ' ')))
        
        # Auto-scroll
        self.table.scrollToBottom()

    def clear_results(self):
        self.table.setRowCount(0)
        self.profiles.clear()

    def _get_default_filename(self, ext):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        return f"facebook_shares_{timestamp}.{ext}"

    def export_csv(self):
        if not self.profiles:
            return
        filename = self._get_default_filename("csv")
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", os.path.join("data", filename), "CSV Files (*.csv)")
        if path:
            if CSVExporter.export(self.profiles, path):
                QMessageBox.information(self, "Export", "CSV Export successful.")

    def export_json(self):
        if not self.profiles:
            return
        filename = self._get_default_filename("json")
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON", os.path.join("data", filename), "JSON Files (*.json)")
        if path:
            if JSONExporter.export(self.profiles, path):
                QMessageBox.information(self, "Export", "JSON Export successful.")

    def export_xlsx(self):
        if not self.profiles:
            return
        filename = self._get_default_filename("xlsx")
        path, _ = QFileDialog.getSaveFileName(self, "Export XLSX", os.path.join("data", filename), "Excel Files (*.xlsx)")
        if path:
            if XLSXExporter.export(self.profiles, path):
                QMessageBox.information(self, "Export", "XLSX Export successful.")
            else:
                QMessageBox.critical(self, "Export", "XLSX Export failed. Is openpyxl installed?")
