from core.session import Session

class Diagnosis:
    def __init__(self, capture, detector, calculator, session, classifier, db):
        self.capture = capture          # VideoCapture
        self.detector = detector        # HandDetector
        self.calculator = calculator    # AngleCalculator
        self.session = session          # Session
        self.classifier = classifier    # Classifier
        self.db = db                    # DatabaseManager
        self.is_running = False         # флаг, активен ли анализ

    def start_analysis(self):
        self.is_running = True
        self.capture.start_capture(0)

    def stop_analysis(self):
        self.is_running = False
        self.detector.forearm_point = None
        self.capture.release()

    def get_current_frame(self):
        return self.capture.get_frame()

    def process_frame(self, frame):
        if not self.is_running:
            return {}, ""
        if frame is None:
            return {}, ""

        landmarks = self.detector.detect_landmarks(frame)
        if landmarks is None:
            return {}, ""

        angle = self.calculator.calculate_all_angles(landmarks)
        diagnosis = self.classifier.classify(angle)

        return angle, diagnosis

    def set_patient(self, patient_id):
        self.session.patient_id = patient_id

    def save_current_session(self):
        self.session.diagnosis = self.classifier.best_diagnosis
        patient_id, diagnosis = self.session.save_to_db()
        self.db.save_diagnostic_result(patient_id, diagnosis)

    def start_new_session(self):
        self.session = Session()
        self.classifier.restart_classifier()