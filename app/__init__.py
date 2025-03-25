import logging
from flask import Flask
from flask_cors import CORS


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)

# Flask App initialization
app = Flask(__name__)
CORS(app)

# Application sessions store
app_sessions = {}

from app import views