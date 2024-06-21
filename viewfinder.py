'''Generate picture frame from display and printing'''

import logging
from threading import Thread

# pylint: disable=no-name-in-module
from cv2 import startWindowThread, namedWindow, setWindowProperty, WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN
from cv2 import copyMakeBorder, addWeighted, flip, imread, imshow, IMREAD_UNCHANGED, BORDER_CONSTANT
# pylint: enable=no-name-in-module

import numpy as np
from pynput.keyboard import Listener

from camera import Camera

class Viewfinder:
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
        '''Start processing pictures'''
        self.running = True

        logging.debug("Retrieving decal pictures")
        self.halo = imread("/root/phoque/assets/img/halo.png", IMREAD_UNCHANGED)
        self.horns = imread("/root/phoque/assets/img/horns.png", IMREAD_UNCHANGED)
        self.decal = self.halo

        self.alpha = np.full((self.HEIGHT, self.WIDTH), 128, dtype=np.uint8)

        logging.debug("Opening preview window")
        startWindowThread()
        namedWindow(self.WINDOW_NAME, WND_PROP_FULLSCREEN)
        setWindowProperty(self.WINDOW_NAME, WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN)
        logging.debug("Rendering")

        self.key_thread = Thread(target=self.listen_for_input)
        self.key_thread.start()

        self.render_thread = Thread(target=self.render_preview)
        self.render_thread.start()


    def render_preview(self):
        '''Display processed picture in window'''
        while self.running:
            frame = self.camera.get_latest_frame()

            # Add a border to fill the screen
            margin = int((self.WIDTH - frame.shape[1]) / 2)
            bordered = copyMakeBorder(src=frame, top=0, bottom=0, left=margin, right=margin, borderType=BORDER_CONSTANT)

            # Add alpha layer (missing from video still)
            bordered_with_alpha = np.dstack((bordered, self.alpha))

            # Combine photo and decal
            combined = addWeighted(bordered_with_alpha, 1, self.decal , 1, 0)

            # Mirror image
            flipped = flip(combined, 1)

            # Display composite image on screen
            imshow(self.WINDOW_NAME, flipped)

            # Remove the border to restore original image dimension
            cropped = flipped[0:flipped.shape[0], margin:flipped.shape[1] - margin, 0:flipped.shape[2]]

            # Make modified image available for print
            self.camera.set_edited_image(cropped)

    def listen_for_input(self):
        '''Listen for keyboard input to change decals'''
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        '''Handle keyboard input'''
        if key.char == "q":
            self.decal = self.halo
        elif key.char == "d":
            self.decal = self.horns