from time import sleep
import click
from camera import Camera
from database import Database
from viewfinder import Viewfinder
from printer import Printer
from composer import Composer, Mode
from gpiozero import Button
from signal import pause
import logging

@click.command()
@click.option("--number", "-n", default=None, help="Override for the ticket number")
@click.option("--reset", "-r", is_flag=True, help="Reset ticket count to 0")
@click.option("--mode", "-m", default="ticket", type=click.Choice(["ticket", "photo"], case_sensitive=False))
def main(number, reset, mode):
    logging.basicConfig(
        level=logging.DEBUG,
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
        print_mode = Mode[mode.lower()]
        
        with Camera() as camera:
            printer = Printer()

            button = Button(23)

            def snap():
                logging.debug("Snap")
                comp.make_ticket(number, camera, printer, print_mode)

            button.when_released = snap
            
            if print_mode == Mode.photo:
                sleep(1)
                
                display = Viewfinder(camera)
                display.start()
            
            logging.info("Initialization complete")

            pause()
    
if __name__ == '__main__':
    main()