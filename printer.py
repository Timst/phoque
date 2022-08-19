import cups
from datetime import datetime

class Printer(object):
    PRINTER = 'pos1'
    connection: cups.Connection
    
    def __init__(self):
        self.connection = cups.Connection()
        
    def print(self, file):
        print(f"{datetime.now()}: Sending print")
        self.connection.printFile(self.PRINTER, file, "Ticket", {})
        print(f"{datetime.now()}: Printing done")