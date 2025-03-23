from flask import render_template, Response, request
import time
from app.utils import get_open_applications

def setup_routes(app):
    # Home page route
    @app.route('/')
    def home():
        curr_apps = get_open_applications()
        return render_template('index.html', curr_apps=curr_apps)

    @app.route('/select-app', methods=['POST'])
    def handle_selection():
        selected_app = request.form.get('application')
        # Here you can add your logic to handle the selected application
        return f'Selected application: {selected_app}'
