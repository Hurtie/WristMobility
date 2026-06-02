import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2

from core.landmark_smoother import EWMASmoother
from queue import Queue

class HandDetector:
    def __init__(self, model_path='models/hand_landmarker.task', num_hands=1):
        self.model_path = model_path
        self.num_hands = num_hands
        self.detector = None
        self.result_queue = Queue(maxsize=1)
        self.smoother = EWMASmoother(alpha=0.2)
        self.forearm_point = None
        self._initialize_detector()

    def _initialize_detector(self):
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=self.num_hands,
            min_hand_detection_confidence=0.8,
            min_hand_presence_confidence=0.8,
            min_tracking_confidence=0.8,
            result_callback=self._callback
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def _callback(self, detection_result, mp_image, timestamp_ms):
        if not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except:
                pass
        self.result_queue.put((detection_result, timestamp_ms))

    def detect_landmarks(self, frame):
        if self.detector is None:
            raise RuntimeError("Детектор не запущен")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(cv2.getTickCount() * 1000 / cv2.getTickFrequency())

        self.detector.detect_async(mp_image, timestamp_ms)

        if not self.result_queue.empty():
            detection_result, _ = self.result_queue.get_nowait()
            if detection_result and detection_result.hand_landmarks:
                hand_landmarks = detection_result.hand_landmarks[0]
                raw_landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks]
                if self.forearm_point is None:
                    new_x = raw_landmarks[0][0] - 1 * (raw_landmarks[9][0] - raw_landmarks[0][0])
                    new_y = raw_landmarks[0][1] - 1 * (raw_landmarks[9][1] - raw_landmarks[0][1])
                    new_z = raw_landmarks[0][2] - 1 * (raw_landmarks[9][2] - raw_landmarks[0][2])
                    self.forearm_point = (new_x, new_y, new_z)
                raw_landmarks.append(self.forearm_point)
                smooth_landmarks = self.smoother.smooth(raw_landmarks)
                return smooth_landmarks
        return None

    def release(self):
        if self.detector:
            self.detector.close()
            self.detector = None