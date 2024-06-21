'''Access/update ticket DB'''

from datetime import datetime
import logging

from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Ticket(Base):
    __tablename__ = 'Tickets'
    ID = Column(Integer, primary_key=True)
    NUMBER = Column(Integer)
    TIMESTAMP_CREATED = Column(DateTime)
    TIMESTAMP_CALLED = Column(DateTime)

class Database:
    CONNECTION_STRING = "sqlite:///phoque.db"
    database: Engine

    def __init__(self):
        self.database = create_engine(self.CONNECTION_STRING)
        Base.metadata.create_all(self.database)

    def insert(self, number: int):
        '''Add a new (uncalled) ticket'''
        entry = Ticket(
            TIMESTAMP_CREATED = datetime.now(),
            NUMBER = number)
        with Session(bind=self.database) as session:
            with session.begin():
                session.add(entry)

    def call(self):
        '''Call the first uncalled ticket (update it to add a TIMESTAMP_CALLED value)'''
        with Session(bind=self.database) as session:
            with session.begin():
                last_called = self.get_latest_called_ticket()

                if last_called is None:
                    to_call = 1
                else:
                    to_call = int(self.get_latest_called_ticket()) + 1

                ticket = session.query(Ticket).where(Ticket.ID == str(to_call)).first()

                if ticket is not None:
                    ticket.TIMESTAMP_CALLED = datetime.now()
                    session.commit()
                    return to_call
                else:
                    logging.warning(f"No number to call, {last_called} is current.")
                    return None

    def get_latest_ticket_number(self):
        '''Get newest ticket number, or 0 if there are no tickets'''
        with Session(bind=self.database) as session:
            with session.begin():
                query = session.query(Ticket).order_by(Ticket.ID.desc()).limit(1).all()

                if any(query):
                    return query[0].NUMBER
                else:
                    return 0

    def get_latest_called_ticket(self):
        '''Get latest called ticket, or None if there are no (called) tickets'''
        with Session(bind=self.database) as session:
            with session.begin():
                query = session.query(Ticket).where(Ticket.TIMESTAMP_CALLED != "NULL").order_by(Ticket.ID.desc()).limit(1).all()

                if any(query):
                    return query[0].NUMBER
                else:
                    return None

    def get_called_tickets_sample(self):
        '''Return the last two (if available) to 15 tickets. If fewer than two tickets, return None'''
        with Session(bind=self.database, expire_on_commit=False) as session:
            with session.begin():
                query = session.query(Ticket).where(Ticket.TIMESTAMP_CALLED != "NULL").order_by(Ticket.ID.desc()).limit(15).all()

                if any(query) and len(query) >= 2:
                    return query
                else:
                    return None

    def reset_ticket_number(self):
        '''Add a new ticket with number 0, "resetting" the queue'''
        with Session(bind=self.database) as session:
            with session.begin():
                session.add(Ticket(
                    TIMESTAMP_CREATED=datetime.now(),
                    NUMBER=0))
