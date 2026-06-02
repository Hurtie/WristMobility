class EWMASmoother:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.smoothed_landmarks = None

    def smooth(self, landmarks):
        if landmarks is None or len(landmarks) != 21:
            return landmarks

        if self.smoothed_landmarks is None:
            self.smoothed_landmarks = list(landmarks)
            return landmarks

        new_smoothed = []
        for i, current_point in enumerate(landmarks):
            prev_smoothed_point = self.smoothed_landmarks[i]

            smoothed_x = self.alpha * current_point[0] + (1 - self.alpha) * prev_smoothed_point[0]
            smoothed_y = self.alpha * current_point[1] + (1 - self.alpha) * prev_smoothed_point[1]
            smoothed_z = self.alpha * current_point[2] + (1 - self.alpha) * prev_smoothed_point[2]
            new_smoothed.append((smoothed_x, smoothed_y, smoothed_z))

        self.smoothed_landmarks = new_smoothed
        return new_smoothed