from threading import Event, Lock, Thread
from flask import Flask, Response, render_template
from humanfriendly import format_timespan
import logging

from admin import Admin
from database import Database

class EndpointAction(object):
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        rep = self.action()
        self.response.response = rep
        return self.response

class Server(object):
    app = Flask(__name__)
    db: Database
    admin: Admin
    stop_event: Event
    
    lock: Lock
    thread: Thread
    
    def __init__(self, db: Database):
        self.db = db
        self.admin = Admin(db)
        
        self.add_endpoint(endpoint="/admin", endpoint_name="admin", handler=self.admin_route)
        self.add_endpoint(endpoint="/public", endpoint_name="public", handler=self.public_route)
        self.add_endpoint(endpoint="/latest-call", endpoint_name="latest", handler=self.latest_route)
        
        self.thread = None
        self.stop_event = Event()
        self.lock = Lock()
        
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        

    def start(self):
        logging.info("Starting Flask server...")
        assert self.thread is None
        self.stop_event.clear()
        self.thread = Thread(target=self.run)
        self.thread.start()
        return self
        
    def run(self):
        self.app.run(host="0.0.0.0")
        
    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))

    def admin_route(self):
        assert self.thread is not None
        with self.lock:
            stats = self.admin.get_stats()
            time_per_crepe = "N/A"
            wait = "N/A"
            
            if stats.time_per_crepe is not None:
                time_per_crepe = format_timespan(stats.time_per_crepe.total_seconds(), detailed=False, max_units=2)
                wait = format_timespan(stats.wait.total_seconds(), detailed=False, max_units=1)
            
            remaining = format_timespan(stats.remaining.total_seconds(), detailed=False, max_units=1)
            
            return render_template(
                'admin.html', 
                current=stats.current, 
                top=stats.top, 
                time_per_crepe=time_per_crepe, 
                depth=stats.depth, 
                wait=wait, 
                remaining=remaining)

    def public_route(self):
        assert self.thread is not None
        with self.lock:
            return render_template('public.html', number=147)

    def latest_route(self):
        assert self.thread is not None
        with self.lock:
            latest_call =  self.db.get_latest_called_ticket()
            
            if latest_call is None:
                return "Welcome!"
            else:
                return str(latest_call)