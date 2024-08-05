'''Handle video input'''
from threading import Thread, Event, Lock
import logging

# pylint: disable=no-name-in-module
from cv2 import VideoCapture, cvtColor, threshold, CAP_PROP_EXPOSURE, COLOR_RGB2GRAY, THRESH_BINARY, THRESH_OTSU
# pylint: enable=no-name-in-module

from PIL import Image
from numpy import ndarray

class Camera:
    FRAMES_TO_CAPTURE = 5
    camera: VideoCapture
    lock: Lock
    thread: Thread
    stop_event: Event
    image: Image
    edited_image: Image
    frame: ndarray

    def __init__(self):
        self.camera = VideoCapture(-1)
        self.camera.set(CAP_PROP_EXPOSURE, -4)
        self.thread = None
        self.stop_event = Event()
        self.lock = Lock()

    def start(self):
        '''Start camera handler (on dedicated thread)'''
        assert self.thread is None
        self.stop_event.clear()
        self.thread = Thread(target=self.run)
        self.thread.start()
        return self

    def stop(self):
        '''Stop camera handler thread'''
        assert self.thread is not None
        assert not self.stop_event.is_set()

        self.stop_event.set()
        self.thread.join()

        self.thread = None

    def __enter__(self, *args, **kwargs):
        return self.start(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        if self.thread is not None:
            self.stop()

    def run(self):
        '''Start receiving frames'''
        while not self.stop_event.wait(0.1):
            result, frame = self.camera.read()

            if result:
                self.frame = frame
                self.image = self.__generate_image(frame)
            else:
                raise RuntimeError("Error while capturing frame")

    def get_latest_image(self, edited: bool):
        '''Get the latest (processed) image'''
        assert self.thread is not None

        with self.lock:
            logging.debug(f"Retrieving {'edited' if edited else ''} image")
            return self.edited_image if edited else self.image

    def get_latest_frame(self):
        '''Get the latest (unprocessed) image'''
        assert self.thread is not None

        with self.lock:
            return self.frame

    def set_edited_image(self, frame):
        '''Set processed image'''
        self.edited_image = self.__generate_image(frame)

    def __generate_image(self, frame):
        '''Process an image'''
        gray_frame = cvtColor(frame, COLOR_RGB2GRAY)
        (thresh, bw_frame) = threshold(gray_frame, 128, 255, THRESH_BINARY | THRESH_OTSU)
        with self.lock:
            return Image.fromarray(bw_frame)