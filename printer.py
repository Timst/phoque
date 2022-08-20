import cups
from datetime import datetime
import logging

class Printer(object):
    PRINTER = 'pos1'
    connection: cups.Connection
    
    def __init__(self):
        self.connection = cups.Connection()
        
    def print(self, file):
        logging.debug("Sending print")
        self.connection.printFile(self.PRINTER, file, "Ticket", {})