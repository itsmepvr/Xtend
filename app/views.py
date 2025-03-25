"""Flask routes for handling application selection, streaming, and session management."""

import uuid
import time
import cv2
from werkzeug.exceptions import HTTPException
from flask import render_template, Response, request, redirect, url_for, jsonify
from app import app, app_sessions, logger
from app.utils import get_open_applications
from app.capture import AppCapturer

@app.route('/')
def index():
    """Render the index page with available applications and active sessions."""
    try:
        applications = get_open_applications()
        logger.info("Rendered index page with current applications.")
        return render_template('index.html', curr_apps=applications, active_sessions=app_sessions)
    except HTTPException as err:  # More specific exception logging
        logger.error("Error rendering index page: %s", err, exc_info=True)
        return jsonify({'error': "Error loading the page"}), 500

@app.route('/select-app', methods=['POST'])
def handle_selection():
    """Handle selection of an application for screen capture."""
    selected_app = request.form.get('application')

    if not selected_app:
        logger.warning("No application selected by the user.")
        return redirect(url_for('index'))

    session_id = str(uuid.uuid4())

    try:
        logger.info("Starting capture for %s with session ID %s", selected_app, session_id)
        capturer = AppCapturer(selected_app)
        capturer.start_capture()

        app_sessions[session_id] = {
            'capturer': capturer,
            'timestamp': time.time(),
            'app_name': selected_app
        }
        logger.info("Capture started successfully for %s, session ID: %s", selected_app, session_id)
        return redirect(url_for('index'))

    except (KeyError, ValueError, RuntimeError) as err:
        logger.error("Failed to start capture for %s: %s", selected_app, err, exc_info=True)
        return redirect(url_for('index'))

@app.route('/stream/<session_id>', methods=['GET'])
def stream_page(session_id):
    """Render the streaming page for a given session."""
    if session_id not in app_sessions:
        logger.error("Invalid session ID: %s requested for streaming.", session_id)
        return "Session expired or invalid", 404

    logger.info("Starting video feed for session ID: %s", session_id)
    return render_template('stream.html', session_id=session_id)

def generate_frames(session_id):
    """Generate video frames for live streaming."""
    while True:
        if session_id not in app_sessions:
            break

        capturer = app_sessions[session_id]['capturer']

        try:
            if capturer.frame is not None:
                ret, buffer = cv2.imencode('.jpg', capturer.frame) # pylint: disable=no-member
                if not ret:
                    logger.warning("Failed to encode frame for session %s", session_id)
                    continue
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')

            time.sleep(0.033)

        except GeneratorExit:
            logger.info("Client disconnected for session %s.", session_id)
            break
        except Exception as err:
            logger.error("Stream error for session %s: %s", session_id, err, exc_info=True)
            break

@app.route('/video_feed/<session_id>')
def video_feed(session_id):
    """Stream the captured video for a session."""
    if session_id not in app_sessions:
        logger.error("Invalid session ID: %s requested for video feed.", session_id)
        return "Invalid session", 404

    logger.info("Streaming video feed for session ID: %s", session_id)
    return Response(generate_frames(session_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/close-session', methods=['POST'])
def close_session():
    """Close an active session."""
    session_id = request.form.get('session_id')

    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400

    if session_id in app_sessions:
        del app_sessions[session_id]
        return redirect('/')

    return jsonify({'error': 'Session not found'}), 404

@app.errorhandler(Exception)
def handle_exception(error):
    """Global error handler for catching unhandled exceptions."""
    logger.error("Uncaught exception: %s", error, exc_info=True)
    return jsonify({'error': "Internal Server Error"}), 500

@app.route("/favicon.ico")
def favicon():
    "Favicon for exception error"
    return "", 200
