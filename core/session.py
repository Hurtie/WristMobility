class Session:
    def __init__(self):
        self.patient_id = None
        self.diagnosis = None

    def save_to_db(self):
        return self.patient_id, self.diagnosis