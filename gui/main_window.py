from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
                             QPushButton, QWidget, QTextEdit, QLineEdit, QMessageBox, QComboBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimedia import QCameraInfo
from gui.results_viewer import ResultsViewer
import cv2

class MainWindow(QMainWindow):
    def __init__(self, diagnosis, db):
        super().__init__()
        self.diagnosis = diagnosis
        self.db = db
        self.setWindowTitle("Диагностика подвижности кисти")
        self.setGeometry(100, 100, 1100, 600)
        self.last_angles = {}
        self.last_classification = "Результат: ---"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.video_label.setFixedSize(640, 480)
        left_layout.addWidget(self.video_label)
        left_layout.addStretch()
        main_layout.addWidget(left_widget, stretch=2)

        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(150)
        self.refresh_cam_btn = QPushButton("Обновить")
        self.refresh_cam_btn.clicked.connect(self.refresh_cameras)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.name_label = QLabel("ФИО пациента:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите фамилию, имя, отчество")
        self.start_btn = QPushButton("Старт")
        self.start_btn.clicked.connect(self.start_analysis)

        name_layout = QVBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(self.start_btn)

        self.angle_label = QLabel("Угол между кистью и предплечьем: ---")
        self.angle_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.result_label = QLabel("Результат: ---")
        self.result_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.save_btn = QPushButton("Сохранить сеанс")
        self.save_btn.clicked.connect(self.save_session)
        self.save_btn.setEnabled(False)

        self.view_btn = QPushButton("Просмотр результатов")
        self.view_btn.clicked.connect(self.view_results)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: green;")

        right_layout.addLayout(name_layout)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.angle_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.result_label)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.save_btn)
        right_layout.addWidget(self.view_btn)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.status_label)
        right_layout.addStretch()

        main_layout.addWidget(right_widget, stretch=1)

        self.timer = QTimer()
        self.refresh_cameras()
        self.timer.timeout.connect(self.update_info)
        self.camera_started = False

    @staticmethod
    def is_valid_fullname(name):
        parts = name.strip().split()
        return len(parts) >= 3

    def start_analysis(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО пациента")
            return
        if not self.is_valid_fullname(name):
            QMessageBox.warning(
                self,
                "Ошибка",
                "ФИО должно содержать минимум три слова (фамилия, имя, отчество)"
            )
            return

        self.diagnosis.start_new_session()
        patient_id = self.db.get_or_create_patient(name)
        self.diagnosis.set_patient(patient_id)

        if self.camera_combo.isEnabled() and self.camera_combo.currentData() is not None:
            camera_id = self.camera_combo.currentData()
        else:
            QMessageBox.warning(self, "Ошибка", "Нет доступных камер")
            return

        if not self.camera_started:
            try:
                self.diagnosis.capture.start_capture(camera_id)
                self.camera_started = True
            except Exception as e:
                QMessageBox.critical(self, "Ошибка камеры", str(e))
                return

        self.diagnosis.start_analysis()
        self.start_btn.setEnabled(False)
        self.name_edit.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.timer.start(30)
        self.status_label.setText("Анализ запущен...")

    def refresh_cameras(self):
        self.camera_combo.clear()
        cameras = QCameraInfo.availableCameras()

        if not cameras:
            self.camera_combo.addItem("Нет доступных камер")
            self.camera_combo.setEnabled(False)
            self.start_btn.setEnabled(False)
        else:
            self.camera_combo.setEnabled(True)
            self.start_btn.setEnabled(True)
            for camera in cameras:
                name = camera.description()
                self.camera_combo.addItem(name, self.camera_combo.currentIndex()+1)

            self.camera_combo.setCurrentIndex(0)

    def update_info(self):
        frame = self.diagnosis.get_current_frame()
        if frame is None:
            return

        connections = [
            (21, 0), (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]

        landmarks = self.diagnosis.detector.detect_landmarks(frame)
        if landmarks:
            h, w = frame.shape[:2]
            for lm in landmarks:
                x, y = int(lm[0] * w), int(lm[1] * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            for i, j in connections:
                if i < len(landmarks) and j < len(landmarks):
                    x1, y1 = int(landmarks[i][0] * w), int(landmarks[i][1] * h)
                    x2, y2 = int(landmarks[j][0] * w), int(landmarks[j][1] * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(bytes(rgb_image.data), int(w), int(h), int(bytes_per_line), QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        angle, classification = self.diagnosis.process_frame(frame)
        if angle:
            self.last_angles = angle
            self.last_classification = classification
            self.angle_label.setText(f"Угол между кистью и предплечьем: {angle:.1f}")
            self.result_label.setText(f"Результат: {classification}")
        else:
            if self.last_angles:
                self.angle_label.setText(f"Угол между кистью и предплечьем: {self.last_angles:.1f}")
            if self.last_classification:
                self.result_label.setText(f"Результат: {self.last_classification}")

    def show_saved(self):
        self.status_label.setText("Сеанс сохранён!")

        QTimer.singleShot(2000, lambda: self.status_label.setText(""))

    def show_error(self, error: str):
        self.result_label.setText(f"Ошибка: {error}")

    def save_session(self):
        try:
            self.diagnosis.save_current_session()
            self.diagnosis.start_new_session()
            self.show_saved()
        except Exception as e:
            self.show_error(f"Не удалось сохранить: {e}")
        finally:
            self.diagnosis.stop_analysis()
            self.timer.stop()
            self.start_btn.setEnabled(True)
            self.name_edit.setEnabled(True)
            self.save_btn.setEnabled(False)

            self.angle_label.clear()
            self.result_label.setText("Результат: ---")

    def view_results(self):
        viewer = ResultsViewer(self.db, self)
        viewer.exec_()

    def closeEvent(self, event):
        self.diagnosis.capture.release()
        event.accept()