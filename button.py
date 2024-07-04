'''Handles the GPIO button logic'''

import logging
import time

from gpiozero import Button as GpioButton

from admin import Admin
from composer import Composer

class Button:
    composer: Composer
    admin: Admin

    button: GpioButton

    last_press_timestamp: float

    def __init__(self, composer: Composer, admin: Admin):
        self.composer = composer
        self.admin = admin
        self.button = GpioButton(23)
        self.last_press_timestamp = None

    def listen(self):
        '''Listen for button taps'''
        self.button.when_released = self.snap

    def snap(self):
        '''Handle button taps'''
        logging.debug("Snap")

        logging.debug(f"Last timestamp: {self.last_press_timestamp}, " +
                      f"current time: {time.time()}, " +
                      f"diff: {'' if self.last_press_timestamp is None else time.time() - self.last_press_timestamp}")

        if self.last_press_timestamp is not None and time.time() - self.last_press_timestamp < 0.5:
            logging.warning("Throttling call.")
        else:
            self.last_press_timestamp = time.time()
            new_ticket =  self.admin.add()

            if new_ticket is not None:
                self.composer.make_ticket(new_ticket)