import math

class AngleCalculator:
    @staticmethod
    def calculate_angle(a, b, c):
        a = (a[0] - b[0], a[1] - b[1])
        b = (c[0] - b[0], c[1] - b[1])
        dot = a[0]*b[0] + a[1]*b[1]
        mag_a = math.hypot(a[0], a[1])
        mag_b = math.hypot(b[0], b[1])
        if mag_a == 0 or mag_b == 0:
            return 0.0
        cos_angle = dot / (mag_a * mag_b)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        return math.degrees(math.acos(cos_angle))

    @staticmethod
    def calculate_all_angles(landmarks):
        if not landmarks or len(landmarks) < 21:
            return {}

        # Индексы ключевых точек
        # Основание кисти 0
        # Большой палец: 1-4
        # Указательный: 5-8
        # Средний: 9-12
        # Безымянный: 13-16
        # Мизинец: 17-20
        angle = AngleCalculator.calculate_angle(landmarks[21], landmarks[0], landmarks[9])
        return angle