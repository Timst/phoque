'''Handles keyboard input to perform admin commands'''

import logging
from threading import Thread
from datetime import datetime

from pynput.keyboard import Listener

from admin import Admin, CallType


class Input:
    admin: Admin
    thread: Thread
    last_pressed_key = None
    reset_timer: datetime
    switch_timer: datetime

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
            logging.debug(f"Key: {key.char}")

            if key.char == "d":
                self.admin.call(call_type=CallType.CALL)

            if key.char == "f":
                self.admin.call(call_type=CallType.REMIND)

            if key.char == "g" and self.last_pressed_key != "g":
                logging.info("Starting switch timer...")
                self.admin.set_switching(True)
                self.switch_timer = datetime.now()

            elif key.char == "h" and self.last_pressed_key != "h":
                logging.info("Starting reset timer...")
                self.admin.set_resetting(True)
                self.reset_timer = datetime.now()

            self.last_pressed_key = key.char


    def on_release(self, key):
        '''Handle keyrelease events'''
        if hasattr(key, "char"):
            if key.char == "h" and self.reset_timer is not None:
                timer = (datetime.now() - self.reset_timer).total_seconds()
                logging.debug(f"Reset timer: {timer}")
                self.admin.set_resetting(False)

                if timer > 3:
                    logging.info("Resetting data")
                    self.admin.reset()

            if key.char == "g" and self.switch_timer is not None:
                timer = (datetime.now() - self.switch_timer).total_seconds()
                logging.debug(f"Switch timer: {timer}")
                self.admin.set_switching(False)

                if timer > 3:
                    logging.info("Switching mode")
                    self.admin.switch()

            self.last_pressed_key = None