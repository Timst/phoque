
import os
import click
from camera import Camera
from printer import Printer
from composer import Composer
from gpiozero import Button
from signal import pause

@click.command()
@click.option("--number", "-n", default=None, help="Override for the ticket number")
@click.option("--restart", "-r", default=None, help="Restart from ticket number 1")
def main(number, restart):
    comp = Composer()

    if restart:
        os.remove(comp.TEMP_FILE)
        
    camera = Camera()
    camera.start()
    
    printer = Printer()

    button = Button(23)

    def snap():
        comp.make_ticket(number, camera, printer)

    button.when_released = snap

    pause()