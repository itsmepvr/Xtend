"Module Configuration"
import os

class Config: # pylint: disable=too-few-public-methods
    "Configuration"
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 4563
    SECRET_KEY = os.getenv("SECRET_KEY", "xtendscreen")

config = Config()
