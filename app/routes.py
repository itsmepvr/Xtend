from flask import render_template, Response, request, redirect, url_for
import time
from app.utils import get_open_applications
from app.capture import AppCapturer
import platform
import uuid
import threading
import time
import cv2

def setup_routes(app, app_sessions):
    # Home page route
    @app.route('/')
    def index():
        applications = get_open_applications()
        return render_template('index.html', 
                            curr_apps=applications,
                            active_sessions=app_sessions)

    @app.route('/select-app', methods=['POST'])
    def handle_selection():
        selected_app = request.form.get('application')
        if not selected_app:
            return redirect(url_for('index'))
        # Generate unique session ID
        session_id = str(uuid.uuid4())
            
        # Start capture session with error handling
        capturer = AppCapturer(selected_app)
        capturer.start_capture()  # This might throw exceptions
            
        # Store session
        app_sessions[session_id] = {
            'capturer': capturer,
            'timestamp': time.time(),
            'app_name': selected_app
        }
            
        return redirect(url_for('index'))
        # try:
        #     # Generate unique session ID
        #     session_id = str(uuid.uuid4())
            
        #     # Start capture session with error handling
        #     capturer = AppCapturer(selected_app)
        #     capturer.start_capture()  # This might throw exceptions
            
        #     # Store session
        #     app_sessions[session_id] = {
        #         'capturer': capturer,
        #         'timestamp': time.time(),
        #         'app_name': selected_app
        #     }
            
        #     return redirect(url_for('index'))
            
        # except Exception as e:
        #     print(f"Failed to start capture: {e}")
        #     return redirect(url_for('index'))

    @app.route('/close-session', methods=['POST'])
    def close_session():
        session_id = request.form.get('session_id')
        if session_id in app_sessions:
            # Proper cleanup
            app_sessions[session_id]['capturer'].stop_capture()
            del app_sessions[session_id]
        return redirect(url_for('index'))

    @app.route('/stream/<session_id>', methods=['GET'])
    def stream_page(session_id):
        # Validate session exists
        if session_id not in app_sessions:
            return "Session expired or invalid", 404
        return render_template('stream.html', session_id=session_id)

    def generate_frames(session_id):
        """Video streaming generator function with proper cleanup"""
        while True:
            if session_id not in app_sessions:
                break
                
            capturer = app_sessions[session_id]['capturer']
            
            try:
                if capturer.frame is not None:
                    ret, buffer = cv2.imencode('.jpg', capturer.frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                          b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    yield (b'--frame\r\n'
                          b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')
                
                time.sleep(0.033)
            except GeneratorExit:
                # Handle client disconnection
                break
            except Exception as e:
                print(f"Stream error: {e}")
                break

    @app.route('/video_feed/<session_id>')
    def video_feed(session_id):
        """Video streaming route with session validation"""
        if session_id not in app_sessions:
            return "Invalid session", 404
            
        return Response(generate_frames(session_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
