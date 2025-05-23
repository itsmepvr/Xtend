"""Flask routes for handling application selection, streaming, and session management."""
import queue
import time
import asyncio
import cv2
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from xtend.app import app, app_sessions, logger, templates
from xtend.utils import get_open_applications, get_local_ip, generate_session_id
from xtend.rs_capture import RustCapturer
from xtend.config import settings

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page with available applications and active sessions."""
    try:
        applications = get_open_applications()
        logger.info("Rendered index page with current applications.")
        server_ip = get_local_ip()
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "curr_apps": applications, 
            "active_sessions": app_sessions,
            "server_ip": server_ip,
            "server_port": settings.PORT,
        })
    except Exception as err:
        logger.error("Error rendering index page: %s", err, exc_info=True)
        return JSONResponse({"error": "Error loading the page"}, status_code=500)

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Render the about page."""
    try:
        logger.info("Rendering about page.")
        return templates.TemplateResponse("about.html", {"request": request})
    except Exception as err:
        logger.error("Error rendering about page: %s", err, exc_info=True)
        return JSONResponse({"error": "Error loading the page"}, status_code=500)

@app.get("/get-applications")
async def get_applications():
    """Get list of open applications with thumbnails."""
    try:
        applications = get_open_applications()
        return JSONResponse({"applications": applications})
    except Exception as err:
        logger.error("Error fetching applications: %s", err, exc_info=True)
        return JSONResponse({"error": "Error fetching applications"}, status_code=500)

@app.get("/get-sessions",)
async def get_sessions():
    """Render the sessions page with available applications and active sessions."""
    try:
        return {"active_sessions": app_sessions}
    except Exception as err:
        logger.error("Error getting active sessions: %s", err, exc_info=True)
        return JSONResponse({"error": "Error getting active sessions"}, status_code=500)

@app.get("/sessions", response_class=HTMLResponse)
async def sessions(request: Request):
    "Render active sessions component"
    try:
        server_ip = get_local_ip()
        return templates.TemplateResponse("sessions.html", {
            "request": request,
            "active_sessions": app_sessions,
            "server_ip": server_ip,
            "server_port": settings.PORT
        })
    except Exception as err:
        logger.error("Error rendering sessions page: %s", err, exc_info=True)
        return JSONResponse({"error": "Error loading the page"}, status_code=500)

# Handle the selection of an application for screen capture
@app.post("/select-app")
async def handle_selection(application: str = Form(...)):
    """Handle selection of an application for screen capture."""
    if not application:
        raise HTTPException(status_code=400, detail="Application is required")

    session_id = str(generate_session_id(app_sessions))

    try:
        logger.info("Starting capture for %s with session ID %s", application, session_id)
        capturer = RustCapturer(application, capture_mode='app')
        capturer.start_capture()

        app_sessions[session_id] = {
            'capturer': capturer,
            'timestamp': time.time(),
            'app_name': application
        }
        logger.info("Capture started successfully for %s, session ID: %s", application, session_id)

        return RedirectResponse(url="/", status_code=303)

    except Exception as err:
        logger.error("Failed to start capture for %s: %s", application, err, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start capture") from err

@app.post("/select-screen")
async def handle_fullscreen_selection():
    """Handle selection of full screen capture."""
    session_id = str(generate_session_id(app_sessions))
    try:
        logger.info("Starting full screen capture with session ID %s", session_id)
        capturer = RustCapturer(capture_mode='full_screen')
        capturer.start_capture()

        app_sessions[session_id] = {
            'capturer': capturer,
            'timestamp': time.time(),
            'app_name': 'Full Screen'
        }
        logger.info("Full screen capture started successfully, session ID: %s", session_id)
        return RedirectResponse(url="/", status_code=303)
    except Exception as err:
        logger.error("Failed to start full screen capture: %s", err, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start full screen capture") from err

# WebSocket endpoint for streaming frames
@app.websocket("/ws/{session_id}")
async def websocket_stream(session_id: str, websocket: WebSocket):
    """Stream the captured video frames to the client via WebSocket."""
    if session_id not in app_sessions:
        logger.error("Invalid session ID: %s requested for streaming.", session_id)
        await websocket.close(code=1000)  # Close connection
        return

    await websocket.accept()
    logger.info("Starting video feed for session ID: %s", session_id)

    try:
        while True:
            capturer = app_sessions[session_id]['capturer']
            frame = None

            # Try to get the latest frame from the frame queue
            try:
                frame = capturer.frame_queue.get_nowait()  # Non-blocking get
            except queue.Empty:
                pass  # No frame available, continue

            if frame is not None:
                # Encode the frame to JPEG format
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    logger.warning("Failed to encode frame for session %s", session_id)
                    continue
                frame_data = buffer.tobytes()
                await websocket.send_bytes(frame_data)  # Send the frame to the client

            else:
                await websocket.send_bytes(b'')  # Send empty bytes if no frame is available

            await asyncio.sleep(0.033)  # ~30 FPS (can be adjusted)

    except WebSocketDisconnect:
        logger.info("Client disconnected for session %s.", session_id)

# Serve the streaming page
@app.get("/stream/{session_id}", response_class=HTMLResponse)
async def stream_page(request: Request, session_id: str):
    """Render the streaming page for a given session."""
    if session_id not in app_sessions:
        logger.error("Invalid session ID: %s requested for streaming.", session_id)
        return templates.TemplateResponse(
            {"request": request, "session_id": session_id},
            "session_expired.html"
        )

    logger.info("Starting video feed for session ID: %s", session_id)
    return templates.TemplateResponse("stream.html", {"request": request, "session_id": session_id})

# Close an active session
@app.post("/close-session")
async def close_session(session_id: str = Form(...)):
    """Close an active session and redirect to the home page."""
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    if session_id in app_sessions:
        del app_sessions[session_id]
        return RedirectResponse(url="/", status_code=303)  # Redirect to home

    raise HTTPException(status_code=404, detail="Session not found")

# Global error handler
@app.exception_handler(Exception)
async def handle_exception(request, error):
    """Global error handler for uncaught exceptions."""
    logger.error("Uncaught exception: %s %s", error, request, exc_info=True)
    return JSONResponse({"error": "Internal Server Error"}, status_code=500)

# Favicon
@app.get("/favicon.ico")
async def favicon():
    """Return empty response for favicon."""
    return JSONResponse(content="", status_code=200)
