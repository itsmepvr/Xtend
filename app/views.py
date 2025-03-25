import uuid
import time
import cv2
from flask import render_template, Response, request, redirect, url_for
from app import app, app_sessions, logger
from app.utils import get_open_applications
from app.capture import AppCapturer


@app.route('/')
def index():
    try:
        applications = get_open_applications()  # Replace with actual function
        logger.info("Rendered index page with current applications.")
        return render_template('index.html', curr_apps=applications, active_sessions=app_sessions)
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return "Error loading the page", 500

# Handle selection of application for capture
@app.route('/select-app', methods=['POST'])
def handle_selection():
    selected_app = request.form.get('application')
    
    if not selected_app:
        logger.warning('No application selected by the user.')
        return redirect(url_for('index'))

    session_id = str(uuid.uuid4())  # Generate a unique session ID
    
    try:
        logger.info(f"Starting capture for {selected_app} with session ID {session_id}")
        # Start capture session (Assuming AppCapturer is defined)
        capturer = AppCapturer(selected_app)
        capturer.start_capture()

        # Store the session
        app_sessions[session_id] = {
            'capturer': capturer,
            'timestamp': time.time(),
            'app_name': selected_app
        }
        logger.info(f"Capture started successfully for {selected_app}, session ID: {session_id}")
        return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Failed to start capture for {selected_app}: {e}")
        return redirect(url_for('index'))

# Close an active session and stop capture
@app.route('/close-session', methods=['POST'])
def close_session():
    session_id = request.form.get('session_id')
    
    if session_id in app_sessions:
        try:
            app_sessions[session_id]['capturer'].stop_capture()
            del app_sessions[session_id]
            logger.info(f"Session {session_id} closed successfully.")
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
    else:
        logger.warning(f"Attempted to close invalid session ID: {session_id}")
    
    return redirect(url_for('index'))

# Stream page for a session
@app.route('/stream/<session_id>', methods=['GET'])
def stream_page(session_id):
    if session_id not in app_sessions:
        logger.error(f"Invalid session ID: {session_id} requested for streaming.")
        return "Session expired or invalid", 404
    logger.info(f"Starting video feed for session ID: {session_id}")
    return render_template('stream.html', session_id=session_id)

# Video stream route - Generates frames for video streaming
def generate_frames(session_id):
    while True:
        if session_id not in app_sessions:
            break  # End the stream if the session is no longer valid
            
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
            logger.info(f"Client disconnected for session {session_id}.")
            break
        except Exception as e:
            logger.error(f"Stream error for session {session_id}: {e}")
            break

# Video feed route - Streams the captured video for a session
@app.route('/video_feed/<session_id>')
def video_feed(session_id):
    if session_id not in app_sessions:
        logger.error(f"Invalid session ID: {session_id} requested for video feed.")
        return "Invalid session", 404
    logger.info(f"Streaming video feed for session ID: {session_id}")
    return Response(generate_frames(session_id), mimetype='multipart/x-mixed-replace; boundary=frame')

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Uncaught exception: {e}")
    return "Internal Server Error", 500