class Classifier:
    def __init__(self):
        self.angles_to_diagnosis = {
            "Свободное движение": 100,
            "Ограниченное движение": 120,
            "Сильное ограничение движения": 150
        }
        self.best_diagnosis = "Сильное ограничение движения"
        self.best_angle = 360

    def classify(self, angle):
        for diagnosis, threshold in self.angles_to_diagnosis.items():
            if angle <= threshold and angle <= self.best_angle:
                self.best_diagnosis = diagnosis
                self.best_angle = angle
                break
        return self.best_diagnosis

    def restart_classifier(self):
        self.best_diagnosis = "Сильное ограничение движения"
        self.best_angle = 360