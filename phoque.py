
from datetime import datetime 
import click
from camera import Camera
from database import Database
from printer import Printer
from composer import Composer
from gpiozero import Button
from signal import pause
import logging

@click.command()
@click.option("--number", "-n", default=None, help="Override for the ticket number")
@click.option("--reset", "-r", is_flag=True, help="Reset ticket count to 0")
def main(number, reset):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("/var/log/phoque.log"),
            logging.StreamHandler()
        ]
    )

    database = Database()
    
    if reset:
        logging.info("Resetting count")
        database.reset_ticket_number()
    else: 
        comp = Composer(database)
        
        with Camera() as camera:
            printer = Printer()

            button = Button(23)

            def snap():
                comp.make_ticket(number, camera, printer)

            button.when_released = snap

            logging.info("Initialization complete")

            pause()
    
if __name__ == '__main__':
    main()