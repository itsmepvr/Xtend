from flask import Flask
from flask_cors import CORS  # Import CORS for cross-origin support
from app.routes import setup_routes

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    app_sessions = {}

    # Set up middleware (for example, logging or simple error handling)
    @app.before_request
    def before_request():
        print("A request is being made!")

    @app.after_request
    def after_request(response):
        print("Request processed")
        return response

    # Enable CORS for all routes (you can configure this as needed)
    CORS(app)

    # Register routes
    setup_routes(app, app_sessions)

    return app
