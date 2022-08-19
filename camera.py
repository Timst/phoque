import cv2 as cv
from PIL import Image
from datetime import datetime
from threading import Thread, Event, Lock

class Camera(object):
    FRAMES_TO_CAPTURE = 5
    camera: cv.VideoCapture
    lock: Lock
    thread: Thread
    stop_event: Event
    image: Image
    
    def __init__(self):
        self.camera = cv.VideoCapture(0)
        self.camera.set(cv.CAP_PROP_EXPOSURE, -4) 
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
            #print(f"{datetime.now()}: Capturing frame")
            result, frame = self.camera.read()
            
            if result:
                bw_frame = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
                with self.lock:
                    self.image = Image.fromarray(bw_frame)
            else:
                raise RuntimeError("Error while capturing frame")
            
    def get_latest_frame(self):
        assert self.thread is not None
        
        with self.lock:
            return self.image