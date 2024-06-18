from sqlalchemy import create_engine, Column, Integer, DateTime, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime
import logging

Base = declarative_base()
        
class Ticket(Base):
    __tablename__ = 'Tickets'
    ID = Column(Integer, primary_key=True)
    NUMBER = Column(Integer)
    TIMESTAMP_CREATED = Column(DateTime)
    TIMESTAMP_CALLED = Column(DateTime)

class Database(object):
    CONNECTION_STRING = "sqlite:///phoque.db"
    database: Engine
    
    def __init__(self):
        self.database = create_engine(self.CONNECTION_STRING)
        Base.metadata.create_all(self.database)
        
    def insert(self, number: int):
        entry = Ticket(
            TIMESTAMP_CREATED = datetime.now(), 
            NUMBER = number)
        with Session(bind=self.database) as session:
            with session.begin():
                session.add(entry)
                
    def call(self):
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
                else:
                    logging.warning(f"No number to call, {last_called} is current.")
                
    def get_latest_ticket_number(self):
        with Session(bind=self.database) as session:
            with session.begin():
                query = session.query(Ticket).order_by(Ticket.ID.desc()).limit(1).all()
                
                if any(query):
                    return query[0].NUMBER
                else:
                    return 0
                
    def get_latest_called_ticket(self):
        with Session(bind=self.database) as session:
            with session.begin():
                query = session.query(Ticket).where(Ticket.TIMESTAMP_CALLED != None).order_by(Ticket.ID.desc()).limit(1).all()
                
                if any(query):
                    return query[0].NUMBER
                else:
                    return None
                
    def get_last_5_called_tickets(self):
        with Session(bind=self.database, expire_on_commit=False) as session:
            with session.begin():
                query = session.query(Ticket).where(Ticket.TIMESTAMP_CALLED != None).order_by(Ticket.ID.desc()).limit(5).all()
                
                if any(query) and len(query) >= 5:
                    return query
                else:
                    return None
                
    def reset_ticket_number(self):
        with Session(bind=self.database) as session:
            with session.begin():
                session.add(Ticket(
                    TIMESTAMP_CREATED=datetime.now(), 
                    NUMBER=0))
                