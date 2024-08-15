'''Compute values for the Admin panel'''

import logging
from enum import Enum
from dataclasses import dataclass
from datetime import timedelta, datetime, date, time
from time import sleep

from playsound import playsound
from pyttsx3 import Engine, init as tts_init
from pyttsx3.voice import Voice
from cachetools import cached, TTLCache

from database import Database

class CallType(Enum):
    CALL = 1
    REMIND = 2
    SKIP = 3

class OpenState(Enum):
    OPEN = 1
    LAST_CALL = 2
    FINISHING = 3
    CLOSED = 4

    def next(self):
        '''Get following state'''
        if self.value == 4:
            return OpenState.OPEN
        else:
            return OpenState(self.value + 1)

@dataclass
class Stats:
    current: int
    top: int
    depth: int
    time_per_crepe: timedelta
    wait: timedelta
    remaining: timedelta
    resetting: bool
    switching: bool
    state: OpenState

class Admin:
    database: Database
    end_of_shift = datetime.combine(date.today(), time(23, 00, 00))

    resetting: bool
    switching: bool

    engine: Engine
    english: Voice
    french: Voice

    stats: Stats

    state: OpenState

    def __init__(self, database: Database):
        self.database = database
        self.engine = tts_init()
        self.engine.setProperty('rate', 130)
        voices = self.engine.getProperty('voices')
        self.english = next(filter(lambda x: x.name == "english-us", voices))
        self.french = next(filter(lambda x: x.name == "french", voices))
        self.resetting = False
        self.switching = False
        self.state = OpenState.OPEN

    @cached(cache=TTLCache(maxsize=1024, ttl=1))
    def get_stats(self):
        '''Return various data on the state of the queue'''
        current = self.database.get_latest_called_ticket()
        top = self.database.get_latest_ticket_number()

        if current is None:
            current = 0

        depth = top - current
        remaining = self.end_of_shift - datetime.now()

        samples = self.database.get_called_tickets_sample()

        time_per_crepe = None
        wait = None

        if samples is not None:
            earliest_ticket = samples[len(samples) - 1]
            latest_ticket = samples[0]

            total_time = latest_ticket.TIMESTAMP_CALLED - earliest_ticket.TIMESTAMP_CALLED
            time_per_crepe = total_time / len(samples)
            wait = time_per_crepe * depth

        return Stats(current, top, depth, time_per_crepe, wait, remaining, self.resetting, self.switching, self.state)

    def add(self):
        '''Add a ticket to the queue (if open)'''
        top = self.database.get_latest_ticket_number()

        if self.state in (OpenState.OPEN, OpenState.LAST_CALL):
            new_number = top + 1
            self.database.insert(new_number)
            return new_number
        else:
            logging.warning(f"Can't add ticket, system is in {self.state.name()} state")
            return None

    def call(self, call_type: CallType):
        '''Make a voice announcement (if calling or reminding) and update called ticket (if calling or skipping)'''
        number = None

        if self.state != OpenState.CLOSED:
            if call_type == CallType.REMIND:
                number = self.database.get_latest_called_ticket()
            else:
                number = self.database.call()

            if number is not None and call_type != CallType.SKIP:
                logging.info(f"{'Calling' if call_type == CallType.CALL else 'Pinging'} ticket {number}")

                playsound("assets/sounds/jingle.wav")

                sleep(0.3)

                self.engine.setProperty('voice', self.english.id)
                self.engine.say(f"Number {number}")
                self.engine.runAndWait()

                sleep(0.3)

                self.engine.setProperty('voice', self.french.id)
                self.engine.say(f"Numéro {number}")
                self.engine.runAndWait()

    def set_switching(self, switch):
        '''Indicate that we're mid switching states'''
        self.switching = switch

    def set_resetting(self, reset):
        '''Indicate that we're mid-reset'''
        self.resetting = reset

    def reset(self):
        '''Switch to a new session'''
        logging.info("Resetting the counts")
        self.database.reset()

        # logging.info("Recreating photo folder")
        # shutil.rmtree(PHOTO_FOLDER)
        # makedirs(PHOTO_FOLDER)

    def switch(self):
        '''Switch to the next mode'''
        next_state = self.state.next()

        logging.info(f"Switching from {self.state.name} to {next_state.name}")

        self.state = next_state