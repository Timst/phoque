'''Handles keyboard input to perform admin commands'''

import logging
from threading import Thread
from datetime import datetime

from pynput.keyboard import Listener

from admin import Admin


class Input:
    admin: Admin
    thread: Thread
    last_pressed_key = None
    reset_timer: datetime

    def __init__(self, admin: Admin):
        self.admin = admin

    def start(self):
        '''Start listening for input (on dedicated thread)'''
        self.thread = Thread(target=self.listen_for_input)
        self.thread.start()

    def listen_for_input(self):
        '''Create keyboard listener'''
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            logging.debug("Listening for input.")
            listener.join()

    def on_press(self, key):
        '''Handle keypress events'''
        if hasattr(key, "char"):
            if key.char == "q":
                self.admin.call()
            elif key.char == "d" and self.last_pressed_key != "d":
                logging.debug("Starting reset timer...")
                self.reset_timer = datetime.now()

            self.last_pressed_key = key.char


    def on_release(self, key):
        '''Handle keyrelease events'''
        if hasattr(key, "char"):
            if key.char == "d":
                timer = (datetime.now() - self.reset_timer).total_seconds()
                logging.debug(f"Reset timer: {timer}")

                if timer > 3:
                    logging.info("Resetting data")

            self.last_pressed_key = None