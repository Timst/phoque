
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
@click.option("--restart", "-r", default=None, help="Restart from ticket number 1")
def main(number, restart):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("/var/log/phoque.log"),
            logging.StreamHandler()
        ]
    )

    database = Database()
    
    if restart:
        database.reset_ticket_number()
    
    comp = Composer(database)
    
    with Camera() as camera:
        printer = Printer()

        button = Button(23)

        def snap():
            logging.info("Printing new ticket")
            comp.make_ticket(number, camera, printer)

        button.when_released = snap

        pause()
    
if __name__ == '__main__':
    main()