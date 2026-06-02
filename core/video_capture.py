import cv2

class VideoCapture:
    def __init__(self):
        self.capture = None
        self.current_source = None

    def start_capture(self, source=0):
        if self.capture is not None:
            self.release()
        self.capture = cv2.VideoCapture(source)
        if not self.capture.isOpened():
            raise RuntimeError(f"Не удалось открыть камеру с идентификатором {source}")
        self.current_source = source

    def get_frame(self):
        if self.capture is None:
            return None
        ret, frame = self.capture.read()
        return frame if ret else None

    def release(self):
        if self.capture:
            self.capture.release()
            self.capture = None
            self.current_source = None