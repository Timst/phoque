'''Phoque entry point'''

import logging
from time import sleep
from signal import pause

import click

from button import Button
from camera import Camera
from database import Database
from input import Input
from viewfinder import Viewfinder
from server import Server
from printer import Printer
from composer import Composer, Mode
from admin import Admin

@click.command()
@click.option("--reset", "-r", is_flag=True, help="Reset ticket count to 0")
@click.option("--mode", "-m", default="ticket", type=click.Choice(["ticket", "photo"], case_sensitive=False))
def main(reset, mode):
    '''App entry point'''
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("/var/log/phoque.log"),
            logging.StreamHandler()
        ]
    )

    database = Database()
    admin = Admin(database)

    if reset:
        logging.info("Resetting count")
        database.reset()
    else:
        print_mode = Mode[mode.upper()]

        with Camera() as camera:
            printer = Printer()
            composer = Composer(database, camera, printer, print_mode)
            button = Button(composer, admin)
            button.listen()

            if print_mode == Mode.PHOTO:
                sleep(1)

                display = Viewfinder(camera)
                display.start()
            elif print_mode == Mode.TICKET:
                server = Server(admin)
                server.start()

                input_handler = Input(admin)
                input_handler.start()

            logging.info("Initialization complete")

            pause()

if __name__ == '__main__':
    main()
