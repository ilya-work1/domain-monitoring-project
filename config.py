import os
from dotenv import load_dotenv
import logging
from datetime import datetime , timedelta

# Load environment variables from .env file
load_dotenv()

class Config:

    # Google OAuth configs
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    CallbackUrl = os.getenv('CallbackUrl')

    # Flask Configuration
    FLASK_HOST = os.getenv('FLASK_HOST')
    FLASK_PORT = int(os.getenv('FLASK_PORT'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG').lower() == 'true'
    
    # Session Configuration
    SESSION_TYPE = os.getenv('SESSION_TYPE')
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv('SESSION_LIFETIME_MINUTES')))

    
    # Session security settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE')
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY')
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE')
    SESSION_REFRESH_EACH_REQUEST = os.getenv('SESSION_REFRESH_EACH_REQUEST')


    # Domain Checking Configuration
    MAX_WORKERS = int(os.getenv('MAX_WORKERS'))
    HTTP_TIMEOUT = int(os.getenv('HTTP_TIMEOUT'))
    SSL_TIMEOUT = int(os.getenv('SSL_TIMEOUT'))
    OVERALL_CHECK_TIMEOUT = int(os.getenv('OVERALL_CHECK_TIMEOUT'))

    # File Storage Configuration
    JSON_DIRECTORY = os.getenv('JSON_DIRECTORY')
    LOGS_DIRECTORY = os.getenv('LOGS_DIRECTORY')

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    DEBUG_LOG_FORMAT = '%(asctime)s - DEBUG - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s'
    ERROR_LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s\n%(exc_info)s'

def setup_logger():
    """Setup logger with daily files"""
    # Create logs directory
    if not os.path.exists(Config.LOGS_DIRECTORY):
        os.makedirs(Config.LOGS_DIRECTORY)

    # Create logger
    logger = logging.getLogger('domain_monitor')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Clear any existing handlers
    logger.handlers = []
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    # App log file (INFO and higher only)
    app_handler = logging.FileHandler(f'{Config.LOGS_DIRECTORY}/app_{current_date}.log')
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(
        Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    ))
    
    # Debug log file (DEBUG level only)
    debug_handler = logging.FileHandler(f'{Config.LOGS_DIRECTORY}/debug_{current_date}.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)  # Only DEBUG messages
    debug_handler.setFormatter(logging.Formatter(
        Config.DEBUG_LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    ))
    
    # Error log file (ERROR and higher only)
    error_handler = logging.FileHandler(f'{Config.LOGS_DIRECTORY}/error_{current_date}.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        Config.ERROR_LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    ))
    
    # Console handler (INFO and higher for cleaner console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    
    # Add handlers
    logger.addHandler(app_handler)
    logger.addHandler(debug_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create logger instance
logger = setup_logger()


