'''Generate tickets/photos'''

from datetime import datetime
from enum import Enum
import logging

from PIL import Image, ImageDraw, ImageFont

from camera import Camera
from printer import Printer
from database import Database

class Mode(Enum):
    '''Phoque operating mode (photobooth or ticket machine)'''
    TICKET = 1
    PHOTO = 2

class Composer:
    '''Generate tickets/photos'''
    TEMP_FILE = "/var/tmp/temp.jpg"
    NUMBER_CACHE = "cache"
    NUMBER_SIZE = 160

    database: Database
    camera: Camera
    printer: Printer
    mode: Mode

    def __init__(self, database: Database, camera: Camera, printer: Printer, mode: Mode):

        self.database = database
        self.camera = camera
        self.printer = printer
        self.mode = mode

    def make_ticket(self, number):
        '''Start generating a ticket'''
        result = False

        if self.mode == Mode.TICKET:
            result = self.generate_ticket(number)
        elif self.mode == Mode.PHOTO:
            result = self.generate_photo()
        else:
            logging.error("Unsupported mode")

        if result:
            self.printer.print(self.TEMP_FILE)
        else:
            logging.warning("No picture available yet")

    def generate_ticket(self, number) -> bool:
        '''Generate a (queue) ticket'''
        title_font_family = "/usr/local/share/fonts/unispace bd.ttf"
        body_font_family = "/usr/local/share/fonts/unispace rg.ttf"

        image = Image.new("L", (800, 800), 255)
        draw = ImageDraw.Draw(image)

        title_font = ImageFont.truetype(title_font_family, 58)
        body_font = ImageFont.truetype(body_font_family, 46)
        side_text_font = ImageFont.truetype(body_font_family, 40)
        number_font = ImageFont.truetype(body_font_family, self.NUMBER_SIZE)

        draw.text((20, 18), "Welcome to Crêpiphany", font = title_font)

        logging.info(f"Printing ticket #{number}")

        digits = len(str(number))

        draw.text((225, 590), "You are number", font=body_font)
        draw.text((390 - (digits * (self.NUMBER_SIZE/4)), 645), str(number), font=number_font)

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

        pic = self.camera.get_latest_image(False)

        if pic is not None:
            image.paste(pic, (80,95))

            image.save(self.TEMP_FILE)
            logging.debug("Image saved")
            return True
        else:
            return False

    def generate_photo(self) -> bool:
        '''Generate a (photobooth) ticket'''
        image = Image.new("L", (800, 650), 255)
        draw = ImageDraw.Draw(image)

        title_font = ImageFont.truetype("/usr/local/share/fonts/LucyTheCat.ttf", 60)

        draw.text((20, 25), "Crêpiphany Fundraiser 2024", font = title_font)

        logging.info("Printing photo")

        pic = self.camera.get_latest_image(True)

        if pic is not None:
            image.paste(pic, (80,130))

            image.save(self.TEMP_FILE)
            logging.debug("Image saved")
            return True
        else:
            return False