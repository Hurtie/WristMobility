from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QLabel, QPushButton, QSplitter, QListWidgetItem, QWidget)
from PyQt5.QtCore import Qt

class ResultsViewer(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Просмотр сохранённых результатов")
        self.setGeometry(200, 200, 900, 600)

        layout = QHBoxLayout(self)

        self.patients_list = QListWidget()
        self.patients_list.itemClicked.connect(self.on_patient_selected)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.results_list = QListWidget()

        right_layout.addWidget(QLabel("Диагностики пациента:"))
        right_layout.addWidget(self.results_list)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        right_layout.addWidget(close_btn)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.patients_list)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])

        layout.addWidget(splitter)

        self.load_patients()

    def load_patients(self):
        patients = self.db.get_all_patients()
        for pid, name in patients:
            item = QListWidgetItem(f"{name} (ID: {pid})")
            item.setData(Qt.ItemDataRole.UserRole, pid)
            self.patients_list.addItem(item)

    def on_patient_selected(self, item):
        patient_id = item.data(Qt.ItemDataRole.UserRole)
        self.results_list.clear()
        results = self.db.get_diagnostic_results_by_patient(patient_id)
        for res in results:
            date = res['date']
            summary = res['result']
            display_text = f"{date} | {summary}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, res)
            self.results_list.addItem(list_item)
