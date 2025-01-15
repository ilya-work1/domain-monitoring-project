from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config, logger
import time

class StickySessionMiddleware:
    def __init__(self, app):
        self.app = app
        self.session_store = {}  # In-memory store instead of Redis
        
    def __call__(self, environ, start_response):
        # Get the session ID directly from environ/cookies
        cookie_header = environ.get('HTTP_COOKIE', '')
        session_id = None
        
        # Parse cookies manually
        if cookie_header:
            cookies = {cookie.split('=')[0].strip(): cookie.split('=')[1].strip() 
                      for cookie in cookie_header.split(';') 
                      if '=' in cookie}
            session_id = cookies.get('STICKY_SESSION_ID')
        
        if session_id:
            # Use in-memory store instead of Redis
            server_id = self.session_store.get(session_id)
            if server_id:
                environ['HTTP_X_STICKY_SERVER'] = server_id
        
        def custom_start_response(status, headers, exc_info=None):
            # Get current server ID
            current_server = environ.get('SERVER_ID', 'default_server')
            
            if session_id:
                # Store in memory instead of Redis
                self.session_store[session_id] = current_server
                # Basic cleanup of old sessions (optional)
                if len(self.session_store) > 10000:  # Arbitrary limit
                    self.session_store.clear()
            
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

def init_sticky_sessions(app):
    """Initialize sticky session handling"""
    # Handle proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Add sticky session middleware
    app.wsgi_app = StickySessionMiddleware(app.wsgi_app)
    
    @app.before_request
    def extend_session():
        from flask import session
        if session:
            session.permanent = True
            app.permanent_session_lifetime = Config.PERMANENT_SESSION_LIFETIME