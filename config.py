import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class Config:

    # Google OAuth configs
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def setup_logger():
    """Setup logger with daily files"""
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create logger
    logger = logging.getLogger('domain_monitor')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers = []
    
    current_date = datetime.now().strftime("%Y%m%d")
    
    # App log file (INFO and higher only)
    app_handler = logging.FileHandler(f'logs/app_{current_date}.log')
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Debug log file (DEBUG level only)
    debug_handler = logging.FileHandler(f'logs/debug_{current_date}.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG)  # Only DEBUG messages
    debug_handler.setFormatter(logging.Formatter(
        '%(asctime)s - DEBUG - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Error log file (ERROR and higher only)
    error_handler = logging.FileHandler(f'logs/error_{current_date}.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s\n%(exc_info)s',
        datefmt='%Y-%m-%d %H:%M:%S'
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


