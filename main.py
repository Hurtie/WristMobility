import sys
from PyQt5.QtWidgets import QApplication

from core.classifier import Classifier
from core.video_capture import VideoCapture
from core.hand_detector import HandDetector
from core.angle_calculator import AngleCalculator
from core.session import Session
from core.database import DatabaseManager
from controller.diagnosis import Diagnosis
from gui.main_window import MainWindow

def main():
    capture = VideoCapture()
    detector = HandDetector(model_path='models/hand_landmarker.task')
    calculator = AngleCalculator()
    classifier = Classifier()
    session = Session()
    db = DatabaseManager("diagnostics.db")

    diagnosis = Diagnosis(capture, detector, calculator, session, classifier, db)

    app = QApplication(sys.argv)
    window = MainWindow(diagnosis, db)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()