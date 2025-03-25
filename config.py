import os

class Config:
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000
    SECRET_KEY = os.getenv("SECRET_KEY", "xtendscreen")

config = Config()
