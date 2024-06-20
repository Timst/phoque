'''Handles communication with the receipt printer'''

import logging

import cups

class Printer:
    PRINTER = 'pos1'
    connection: cups.Connection

    def __init__(self):
        self.connection = cups.Connection()

    def print(self, file):
        '''Send file for printing'''
        logging.debug("Sending print")
        self.connection.printFile(self.PRINTER, file, "Ticket", {})