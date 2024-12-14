import logging
import os
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(current_dir, 'functions test.log')


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

url='http://ec2-54-200-248-130.us-west-2.compute.amazonaws.com:8080'
test_email=os.getenv('test_email')
test_password=os.getenv('test_password')