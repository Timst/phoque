import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

from camera import Camera
from printer import Printer
from database import Database

class Composer(object):
    TEMP_FILE = "temp/temp.jpg"
    NUMBER_CACHE = "cache"
    
    database: Database
    number: int
    last_print_timestamp: float
    
    def __init__(self, database: Database):
        self.number = 1
        self.database = database
        self.last_print_timestamp = None
    
    def make_ticket(self, forced_number: int, camera: Camera, printer: Printer):
        if self.last_print_timestamp is not None and time.time() - self.last_print_timestamp < 1:
            print(f"{datetime.now()}: Throttling call.")
        else:          
            self.last_print_timestamp = time.time()
            print(f"{datetime.now()}: Starting rendering")
            image = Image.new("L", (800, 800), 255)
            print(f"{datetime.now()}: Image created")
            draw = ImageDraw.Draw(image)
            titleFont = ImageFont.truetype("FreeSansBold.ttf", 40)
            yourNumberFont = ImageFont.truetype("FreeSansBold.ttf", 35)
            numberFont = ImageFont.truetype("FreeSansBold.ttf", 120)
            draw.text((150, 15), "Welcome to The BROTHel", font = titleFont)
            print(f"{datetime.now()}: Title drawn")
            ticket_number = forced_number
            
            if forced_number is not None:
                ticket_number = forced_number
            elif self.number is None:
                self.number = self.database.get_latest_ticket_number()
                ticket_number = self.number
            else:
                ticket_number = self.number

            print(f"Drawing number {ticket_number}")
            
            draw.text((265, 600), "You are number", font=yourNumberFont)
            draw.text((365, 665), str(ticket_number), font=numberFont)
            
            print(f"{datetime.now()}: Subtitles drawn")
            
            pic = camera.get_latest_frame()
            
            print(f"{datetime.now()}: Frame retrieved")
            
            if pic is not None:
                image.paste(pic, (80,80))
                print(f"{datetime.now()}: Pic pasted")
                
                image.save(self.TEMP_FILE)
                print(f"{datetime.now()}: Image saved")
                printer.print(self.TEMP_FILE)
                self.increment_number()
            else:
                print("No picture available yet")
        
    def increment_number(self):
        self.database.insert(self.number)
        self.number += 1
