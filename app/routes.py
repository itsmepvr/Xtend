from flask import render_template, Response, request
import time
from app.utils import get_open_applications, AppCapturer
import platform
import uuid
import threading
import time
import cv2

def setup_routes(app, app_sessions):
    # Home page route
    @app.route('/')
    def home():
        curr_apps = get_open_applications()
        return render_template('index.html', curr_apps=curr_apps)

    @app.route('/select-app', methods=['POST'])
    def handle_selection():
        selected_app = request.form.get('application')
        # session_id = str(uuid.uuid4())
        session_id = "abcd"
        
        # Start capture session
        capturer = AppCapturer(selected_app)
        capturer.start_capture()
        
        # Store session
        app_sessions[session_id] = {
            'capturer': capturer,
            'timestamp': time.time()
        }
        
        return f'https://localhost:5000/stream/{session_id}'


    @app.route('/stream/<session_id>', methods=['GET'])
    def stream_page(session_id):
        return render_template('stream.html', session_id=session_id)

    def generate_frames(session_id):
        """Video streaming generator function"""
        while True:
            if session_id not in app_sessions:
                break
                
            capturer = app_sessions[session_id]['capturer']
            if capturer.frame is not None:
                ret, buffer = cv2.imencode('.jpg', capturer.frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.033)

    @app.route('/video_feed/<session_id>')
    def video_feed(session_id):
        """Video streaming route"""
        return Response(generate_frames(session_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
