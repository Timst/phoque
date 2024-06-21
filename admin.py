'''Compute values for the Admin panel'''

import logging
from dataclasses import dataclass
from datetime import timedelta, datetime, date, time
from time import sleep

from playsound import playsound
from pyttsx3 import Engine, init as tts_init
from pyttsx3.voice import Voice
from cachetools import cached, TTLCache

from database import Database

@dataclass
class Stats:
    current: int
    top: int
    depth: int
    time_per_crepe: timedelta
    wait: timedelta
    remaining: timedelta
    resetting: bool

class Admin:
    database: Database
    end_of_shift = datetime.combine(date.today(), time(23, 00, 00))
    resetting: bool

    engine: Engine
    english: Voice
    french: Voice

    stats: Stats

    def __init__(self, database: Database):
        self.database = database
        self.engine = tts_init()
        self.engine.setProperty('rate', 130)
        voices = self.engine.getProperty('voices')
        self.english = next(filter(lambda x: x.name == "english-us", voices))
        self.french = next(filter(lambda x: x.name == "french", voices))
        self.resetting = False

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

        return Stats(current, top, depth, time_per_crepe, wait, remaining, self.resetting)

    def call(self, remind):
        '''Make a voice announcement and update called ticket (don't update if remind = true)'''

        logging.info("Calling ticket")
        number = None

        if not remind:
            number = self.database.call()

        if number is not None:
            playsound("assets/sounds/jingle.wav")

            sleep(0.3)

            self.engine.setProperty('voice', self.english.id)
            self.engine.say(f"Number {number}")
            self.engine.runAndWait()

            sleep(0.3)

            self.engine.setProperty('voice', self.french.id)
            self.engine.say(f"Numéro {number}")
            self.engine.runAndWait()

    def set_resetting(self, reset):
        '''Indicate that we're mid-reset'''
        self.resetting = reset

    def reset(self):
        '''Switch to a new session'''
        logging.info("Resetting the counts")
        self.database.reset()