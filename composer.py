import time
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from enum import Enum

from camera import Camera
from printer import Printer
from database import Database

class Mode(Enum):
    ticket = 1
    photo = 2

class Composer(object):
    TEMP_FILE = "/var/tmp/temp.jpg"
    NUMBER_CACHE = "cache"
    NUMBER_SIZE = 160
    
    database: Database
    number: int
    last_print_timestamp: float
    
    def __init__(self, database: Database):
        self.number = None
        self.database = database
        self.last_print_timestamp = None
    
    def make_ticket(self, forced_number: int, camera: Camera, printer: Printer, mode: Mode):
        logging.debug(f"Last timestamp: {self.last_print_timestamp} current time: {time.time()}, diff: {'' if self.last_print_timestamp is None else time.time() - self.last_print_timestamp}")
        if self.last_print_timestamp is not None and time.time() - self.last_print_timestamp < 1:
            logging.warning("Throttling call.")
        else:
            result = False
            
            self.last_print_timestamp = time.time()
            
            if mode == Mode.ticket:
                result = self.generate_ticket(forced_number, camera)
            elif mode == Mode.photo:
                result = self.generate_photo(camera)
            else:
                logging.error("Unsupported mode")
            
            if result:
                printer.print(self.TEMP_FILE)
                if mode == Mode.ticket:
                    self.increment_number()
            else:
                logging.warning("No picture available yet")
                
    def generate_ticket(self, forced_number: int, camera: Camera) -> bool:
        title_font_family = "/usr/local/share/fonts/unispace bd.ttf"
        body_font_family = "/usr/local/share/fonts/unispace rg.ttf"
         
        image = Image.new("L", (800, 800), 255)
        draw = ImageDraw.Draw(image)

        title_font = ImageFont.truetype(title_font_family, 58)
        body_font = ImageFont.truetype(body_font_family, 46)
        side_text_font = ImageFont.truetype(body_font_family, 40)
        number_font = ImageFont.truetype(body_font_family, self.NUMBER_SIZE)

        draw.text((20, 18), "Welcome to Crêpiphany", font = title_font)

        ticket_number = forced_number
        
        if forced_number is not None:
            ticket_number = forced_number
        elif self.number is None:
            db_number = self.database.get_latest_ticket_number()
            if db_number is None:
                self.number = 1
            else:
                self.number = self.database.get_latest_ticket_number() + 1
            ticket_number = self.number
        else:
            ticket_number = self.number

        logging.info(f"Printing ticket #{ticket_number}")

        digits = len(str(ticket_number))
        
        draw.text((225, 590), "You are number", font=body_font)
        draw.text((390 - (digits * (self.NUMBER_SIZE/4)), 645), str(ticket_number), font=number_font)     

        left_text = Image.new("L", (520, 50), 255)
        left_text_draw = ImageDraw.Draw(left_text)
        left_text_draw.text((0, 0), "2024 Fundraiser", font=side_text_font)       
        rotated_left_text = left_text.rotate(90, expand=True)

        right_text = Image.new("L", (520, 50), 255)
        right_text_draw = ImageDraw.Draw(right_text)
        formatted_time = datetime.now().strftime("%A %H:%M:%S")
        right_text_draw.text((0, 0), formatted_time, font=side_text_font)
        rotated_right_text = right_text.rotate(270, expand=True)

        image.paste(rotated_left_text, (16, 97))
        image.paste(rotated_right_text, (733, 135))
        
        pic = camera.get_latest_image(False)
        
        if pic is not None:
            image.paste(pic, (80,95))
            
            image.save(self.TEMP_FILE)
            logging.debug("Image saved")
            return True
            
    def generate_photo(self, camera: Camera) -> bool:
        image = Image.new("L", (800, 650), 255)
        draw = ImageDraw.Draw(image)

        title_font = ImageFont.truetype("/usr/local/share/fonts/LucyTheCat.ttf", 60)

        draw.text((20, 25), "Crêpiphany Fundraiser 2024", font = title_font)

        logging.info("Printing photo")
        
        pic = camera.get_latest_image(True)
        
        if pic is not None:
            image.paste(pic, (80,130))
            
            image.save(self.TEMP_FILE)
            logging.debug("Image saved")
            return True
        
                
    def increment_number(self):
        self.database.insert(self.number)
        self.number += 1
