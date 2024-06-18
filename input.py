from threading import Thread
from database import Database
from pynput.keyboard import Listener
from datetime import datetime
import logging

class Input(object):
    db: Database
    thread: Thread
    last_pressed_key = None
    
    def __init__(self, db: Database):
        self.db = db
    
    def start(self):
        self.thread = Thread(target=self.listen_for_input)
        self.thread.start()
    
    def listen_for_input(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            logging.debug("Listening for input.")
            listener.join()
                
    def on_press(self, key):
        if hasattr(key, "char"):
            if key.char == "q":
                logging.info("Calling ticket")
                self.db.call()
            elif key.char == "d" and self.last_pressed_key != "d":
                logging.debug("Starting reset timer...")
                self.reset_timer = datetime.now()
            
            self.last_pressed_key = key.char
            
            
    def on_release(self, key):
        if hasattr(key, "char"):
            if key.char == "d":
                timer = (datetime.now() - self.reset_timer).total_seconds()
                logging.debug(f"Reset timer: {timer}")
                
                if timer > 3:
                    logging.info("Resetting data")
                    
            self.last_pressed_key = None