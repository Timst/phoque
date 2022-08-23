import time
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from camera import Camera
from printer import Printer
from database import Database

class Composer(object):
    TEMP_FILE = "/var/tmp/temp.jpg"
    NUMBER_CACHE = "cache"
    TITLE_FONT_FAMILY = "/usr/local/share/fonts/unispace bd.ttf"
    BODY_FONT_FAMILY = "/usr/local/share/fonts/unispace rg.ttf"
    NUMBER_SIZE = 160
    
    database: Database
    number: int
    last_print_timestamp: float
    
    def __init__(self, database: Database):
        self.number = None
        self.database = database
        self.last_print_timestamp = None
    
    def make_ticket(self, forced_number: int, camera: Camera, printer: Printer):
        if self.last_print_timestamp is not None and time.time() - self.last_print_timestamp < 1:
            logging.warning("Throttling call.")
        else:
            self.last_print_timestamp = time.time()
            image = Image.new("L", (800, 800), 255)
            draw = ImageDraw.Draw(image)

            title_font = ImageFont.truetype(self.TITLE_FONT_FAMILY, 58)
            body_font = ImageFont.truetype(self.BODY_FONT_FAMILY, 46)
            side_text_font = ImageFont.truetype(self.BODY_FONT_FAMILY, 40)
            number_font = ImageFont.truetype(self.BODY_FONT_FAMILY, self.NUMBER_SIZE)

            draw.text((20, 18), "Welcome to The BROTHel", font = title_font)
 
            ticket_number = forced_number
            
            if forced_number is not None:
                ticket_number = forced_number
            elif self.number is None:
                self.number = self.database.get_latest_ticket_number() + 1
                ticket_number = self.number
            else:
                ticket_number = self.number

            logging.info(f"Printing ticket #{ticket_number}")

            digits = len(str(ticket_number))
            
            draw.text((225, 590), "You are number", font=body_font)
            draw.text((390 - (digits * (self.NUMBER_SIZE/4)), 645), str(ticket_number), font=number_font)     

            left_text = Image.new("L", (450, 50), 255)
            left_text_draw = ImageDraw.Draw(left_text)
            left_text_draw.text((0, 0), "2022 Waking Dreams", font=side_text_font)       
            rotated_left_text = left_text.rotate(90, expand=True)

            right_text = Image.new("L", (400, 50), 255)
            right_text_draw = ImageDraw.Draw(right_text)
            formatted_time = datetime.now().strftime("%A %H:%M:%S")
            right_text_draw.text((0, 0), formatted_time, font=side_text_font)
            rotated_right_text = right_text.rotate(270, expand=True)

            image.paste(rotated_left_text, (16, 97))
            image.paste(rotated_right_text, (733, 135))
            
            pic = camera.get_latest_frame()
            
            if pic is not None:
                image.paste(pic, (80,95))
                
                image.save(self.TEMP_FILE)
                logging.debug("Image saved")

                printer.print(self.TEMP_FILE)
                self.increment_number()
            else:
                logging.warning("No picture available yet")
        
    def increment_number(self):
        self.database.insert(self.number)
        self.number += 1
