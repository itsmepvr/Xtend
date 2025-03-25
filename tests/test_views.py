"Pytest Test Cases"
import unittest
from unittest.mock import patch
from app import app, app_sessions

class FlaskAppTests(unittest.TestCase):
    """Test Application"""
    def setUp(self):
        """Set up the test client before each test"""
        self.client = app.test_client()  # Flask test client

    def test_index_route(self):
        """Test the index route ('/')"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Select an Application", response.data)

    def test_select_app_route(self):
        """Test the select-app route ('/select-app')"""
        data = {'application': 'my_app'}
        with patch('app.views.AppCapturer') as mock_capturer:
            mock_capturer = mock_capturer.return_value
            mock_capturer.start_capture.return_value = None

            response = self.client.post('/select-app', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertIn('/', response.headers['Location'])

    def test_select_app_route_no_app(self):
        """Test the select-app route with no application selected"""
        data = {'application': ''}
        with patch('app.views.AppCapturer') as mock_capturer:
            mock_capturer = mock_capturer.return_value
            mock_capturer.start_capture.return_value = None

            response = self.client.post('/select-app', data=data)

            self.assertEqual(response.status_code, 302)
            self.assertIn('/', response.headers['Location'])

    def test_close_session_route(self):
        """Test the close-session route ('/close-session')"""
        session_id = '12345'
        app_sessions[session_id] = {
            'capturer': None,
            'timestamp': 0,
            'app_name': 'TestApp'
        }
        data = {'session_id': session_id}
        response = self.client.post('/close-session', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.headers['Location'])

    def test_invalid_session_video_feed(self):
        """Test invalid session for video feed ('/video_feed/<session_id>')"""
        session_id = 'invalid_session_id'
        response = self.client.get(f'/video_feed/{session_id}')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Invalid session", response.data)

    def test_invalid_session_stream_page(self):
        """Test invalid session for stream page ('/stream/<session_id>')"""
        session_id = 'invalid_session_id'
        response = self.client.get(f'/stream/{session_id}')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Session expired or invalid", response.data)

    def test_close_session_no_session_id(self):
        """Test closing a session with no session_id"""
        response = self.client.post('/close-session', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Session ID is required", response.data)

    def test_close_session_not_found(self):
        """Test closing a session that doesn't exist in app_sessions"""
        session_id = 'non_existent_session'
        data = {'session_id': session_id}
        response = self.client.post('/close-session', data=data)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Session not found", response.data)

    def test_stream_session_not_found(self):
        """Test attempting to stream a non-existent session"""
        session_id = 'non_existent_session'
        response = self.client.get(f'/video_feed/{session_id}')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Invalid session", response.data)

    def test_stream_page_session_not_found(self):
        """Test attempting to view the stream page for a non-existent session"""
        session_id = 'non_existent_session'
        response = self.client.get(f'/stream/{session_id}')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Session expired or invalid", response.data)

    def test_favicon(self):
        """Test the favicon route ('/favicon.ico')"""
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"")
