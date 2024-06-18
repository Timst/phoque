from dataclasses import dataclass
from datetime import timedelta, datetime, date, time
from database import Database

@dataclass
class Stats(object):
    current: int
    top: int
    depth: int
    time_per_crepe: timedelta
    wait: timedelta
    remaining: timedelta

class Admin(object):
    db: Database
    end_of_shift = datetime.combine(date.today(), time(23, 00, 00))
    reset_timer = None;
    
    def __init__(self, db: Database):
        self.db = db
        
    def get_stats(self):
        current = self.db.get_latest_called_ticket()
        top = self.db.get_latest_ticket_number()
        
        if current is None:
            current = 0
        
        depth = top - current       
        remaining = self.end_of_shift - datetime.now()
        
        samples = self.db.get_last_5_called_tickets()
        
        time_per_crepe = None
        wait = None
        
        if samples is not None:
            earliest_ticket = samples[4]
            latest_ticket = samples[0]
            
            total_time = latest_ticket.TIMESTAMP_CALLED - earliest_ticket.TIMESTAMP_CALLED
            time_per_crepe = total_time / 5
            wait = time_per_crepe * depth
            
        return Stats(current, top, depth, time_per_crepe, wait, remaining)