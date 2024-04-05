import cv2
from camera import Camera
import logging
import numpy as np
from pynput.keyboard import Listener
from threading import Thread

class Viewfinder(object):
    WIDTH: int = 800
    HEIGHT: int = 480
    WINDOW_NAME: str = "preview"
    
    camera: Camera
    alpha: np.ndarray
    
    decal: np.ndarray
    halo: np.ndarray
    horns: np.ndarray
    
    key_thread: Thread
    render_thread: Thread
    
    running: bool
    
    def __init__(self, camera: Camera):
        self.camera = camera
        
    def start(self):
            self.running = True
            
            logging.debug("Retrieving decal pictures")
            self.halo = cv2.imread("halo.png", cv2.IMREAD_UNCHANGED)
            self.horns = cv2.imread("horns.png", cv2.IMREAD_UNCHANGED)
            self.decal = self.halo
            
            self.alpha = np.full((self.HEIGHT, self.WIDTH), 128, dtype=np.uint8)
            
            logging.debug("Opening preview window")
            cv2.startWindowThread()
            cv2.namedWindow(self.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            logging.debug("Rendering")
            
            self.key_thread = Thread(target=self.listen_for_input)
            self.key_thread.start()
            
            self.render_thread = Thread(target=self.render_preview)
            self.render_thread.start()
            
    
    def render_preview(self):
        while self.running:
            frame = self.camera.get_latest_frame()
            
            # Add a border to fill the screen    
            margin = int((self.WIDTH - frame.shape[1]) / 2)
            bordered = cv2.copyMakeBorder(src=frame, top=0, bottom=0, left=margin, right=margin, borderType=cv2.BORDER_CONSTANT)
            
            # Add alpha layer (missing from video still)
            bordered_with_alpha = np.dstack((bordered, self.alpha))
            
            # Combine photo and decal
            combined = cv2.addWeighted(bordered_with_alpha, 1, self.decal , 1, 0)
            
            # Mirror image
            flip = cv2.flip(combined, 1)    
            
            # Display composite image on screen
            cv2.imshow(self.WINDOW_NAME, flip)
            
            # Remove the border to restore original image dimension
            cropped = flip[0:flip.shape[0], margin:flip.shape[1] - margin, 0:flip.shape[2]]

            # Make modified image available for print    
            self.camera.set_edited_image(cropped)
            
    def listen_for_input(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()
                
    def on_press(self, key):
        if key.char == "q":
            self.decal = self.halo
        elif key.char == "d":
            self.decal = self.horns