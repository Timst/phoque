import cv2
from PIL import Image
from threading import Thread, Event, Lock
import logging
from numpy import ndarray

class Camera(object):
    FRAMES_TO_CAPTURE = 5
    camera: cv2.VideoCapture
    lock: Lock
    thread: Thread
    stop_event: Event
    image: Image
    edited_image: Image
    frame: ndarray
    
    def __init__(self):
        self.camera = cv2.VideoCapture(-1)
        self.camera.set(cv2.CAP_PROP_EXPOSURE, -4) 
        self.thread = None
        self.stop_event = Event()
        self.lock = Lock()
        
    def start(self):
        assert self.thread is None
        self.stop_event.clear()
        self.thread = Thread(target=self.run)
        self.thread.start()
        return self
    
    def stop(self):
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
        while not self.stop_event.wait(0.1):
            result, frame = self.camera.read()
            
            if result:
                self.frame = frame
                self.image = self.__generate_image(frame)
            else:
                raise RuntimeError("Error while capturing frame")
            
    def get_latest_image(self, edited: bool):
        assert self.thread is not None
        
        with self.lock:
            logging.debug(f"Retrieving {'edited' if edited else ''} image")           
            return self.edited_image if edited else self.image
        
    def get_latest_frame(self):
        assert self.thread is not None
        
        with self.lock:
            return self.frame
        
    def set_edited_image(self, frame):
        self.edited_image = self.__generate_image(frame)
        
    def __generate_image(self, frame):
        bw_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        with self.lock:
            return Image.fromarray(bw_frame)