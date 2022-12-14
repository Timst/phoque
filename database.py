from sqlalchemy import create_engine, Column, Integer, DateTime, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime

Base = declarative_base()
        
class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    number = Column(Integer)

class Database(object):
    CONNECTION_STRING = "sqlite:///phoque.db"
    database: Engine
    
    def __init__(self):
        self.database = create_engine(self.CONNECTION_STRING)
        Base.metadata.create_all(self.database)
        
    def insert(self, number: int):
        entry = Ticket(
            time=datetime.now(), 
            number=number)
        with Session(bind=self.database) as session:
            with session.begin():
                session.add(entry)
                
    def get_latest_ticket_number(self):
        with Session(bind=self.database) as session:
            with session.begin():
                query = session.query(Ticket).order_by(Ticket.id.desc()).limit(1).all()
                
                if any(query):
                    return query[0].number
                else:
                    return 1
                
    def reset_ticket_number(self):
        with Session(bind=self.database) as session:
            with session.begin():
                session.add(Ticket(
                    time=datetime.now(), 
                    number=0))