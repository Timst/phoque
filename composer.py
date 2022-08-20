import time
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from camera import Camera
from printer import Printer
from database import Database

class Composer(object):
    TEMP_FILE = "temp/temp.jpg"
    NUMBER_CACHE = "cache"
    TITLE_FONT_FAMILY = "/usr/local/share/fonts/unispace bd.ttf"
    BODY_FONT_FAMILY = "/usr/local/share/fonts/unispace rg.ttf"
    NUMBER_SIZE = 130
    
    database: Database
    number: int
    last_print_timestamp: float
    
    def __init__(self, database: Database):
        self.number = 1
        self.database = database
        self.last_print_timestamp = None
    
    def make_ticket(self, forced_number: int, camera: Camera, printer: Printer):
        if self.last_print_timestamp is not None and time.time() - self.last_print_timestamp < 1:
            logging.warning("Throttling call.")
        else:
            logging.debug("Starting rendering")

            image = Image.new("L", (800, 800), 255)
            draw = ImageDraw.Draw(image)

            titleFont = ImageFont.truetype(self.TITLE_FONT_FAMILY, 44)
            yourNumberFont = ImageFont.truetype(self.BODY_FONT_FAMILY, 32)
            numberFont = ImageFont.truetype(self.BODY_FONT_FAMILY, self.NUMBER_SIZE)

            draw.text((115, 15), "Welcome to The BROTHel", font = titleFont)
 
            ticket_number = forced_number
            
            if forced_number is not None:
                ticket_number = forced_number
            elif self.number is None:
                self.number = self.database.get_latest_ticket_number()
                ticket_number = self.number
            else:
                ticket_number = self.number

            logging.debug(f"Drawing number {ticket_number}")

            digits = len(str(ticket_number))
            
            draw.text((265, 590), "You are number", font=yourNumberFont)
            draw.text((390 - (digits * (self.NUMBER_SIZE/4)), 645), str(ticket_number), font=numberFont)     
            
            pic = camera.get_latest_frame()
            
            if pic is not None:
                image.paste(pic, (80,80))
                
                image.save(self.TEMP_FILE)
                logging.debug("Image saved")

                printer.print(self.TEMP_FILE)
                self.increment_number()
            else:
                logging.warning("No picture available yet")
        
    def increment_number(self):
        self.database.insert(self.number)
        self.number += 1
