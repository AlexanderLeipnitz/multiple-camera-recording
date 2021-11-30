from threading import Thread, Lock
import cv2
from time import time
from logging import debug, info


class VideoCapture:
    def __init__(self, src, backend=None):
        self.stream = cv2.VideoCapture(src, backend)
        self.started = False
        self.read_lock = Lock()

    def read_first_frame(self):
        # self.stream[cam_idx].set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.stream[cam_idx].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.stream.read()
        if self.grabbed:
            return self.frame
        else:
            return None

    def start(self):
        if self.started:
            info("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            self.time = time()
            grabbed, frame = self.stream.read()
            if grabbed:
                self.read_lock.acquire()
                self.grabbed, self.frame = grabbed, frame
                self.read_lock.release()
            debug(
                "Videocapturing Thread took {:.2f} ms.".format(
                    (time() - self.time) * 1000
                )
            )

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        if self.thread.is_alive():
            self.thread.join()

    def get_size(self):
        w = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return [w, h]

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()
