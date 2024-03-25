import cv2
from camera import Camera
import logging
import numpy as np
import time

class Display(object):
    WIDTH: int = 800
    HEIGHT: int = 480
    WINDOW_NAME: str = "preview"
    
    camera: Camera
    halo: np.ndarray
    alpha: np.ndarray
    
    def __init__(self, camera: Camera):
        self.camera = camera
        
    def start(self):
            logging.debug("Retrieving halo pictures")
            self.halo = cv2.imread("halo.png", cv2.IMREAD_UNCHANGED)
            self.alpha = np.full((self.HEIGHT, self.WIDTH), 128, dtype=np.uint8)
            
            logging.debug("Opening preview window")
            cv2.startWindowThread()
            cv2.namedWindow(self.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            logging.debug("Rendering")
            
            while True:
                t1 = time.perf_counter_ns()
                frame = self.camera.get_latest_frame()
                t2 = time.perf_counter_ns()
                logging.debug(f"Getting frame: {int((t2 - t1)/1000000)}ms")
                
                margin = int((self.WIDTH - frame.shape[1]) / 2)
                bordered = cv2.copyMakeBorder(src=frame, top=0, bottom=0, left=margin, right=margin, borderType=cv2.BORDER_CONSTANT)
                t1 = time.perf_counter_ns()
                logging.debug(f"Making border: {int((t1 - t2)/1000000)}ms")
                
                bordered_with_alpha = np.dstack((bordered, self.alpha))
                t1 = time.perf_counter_ns()
                logging.debug(f"Adding alpha: {int((t1 - t2)/1000000)}ms")
                          
                added_image = cv2.addWeighted(bordered_with_alpha, 1, self.halo , 1, 0)
                t2 = time.perf_counter_ns()
                logging.debug(f"Adding: {int((t2 - t1)/1000000)}ms")
                
                cv2.imshow(self.WINDOW_NAME, added_image)
                t1 = time.perf_counter_ns()
                logging.debug(f"Rendering: {int((t1 - t2)/1000000)}ms")
                
                self.camera.set_edited_image(added_image)
                t2 = time.perf_counter_ns()
                logging.debug(f"Saving to camera: {int((t1 - t2)/1000000)}ms")