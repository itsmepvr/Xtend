"PyTest"
import unittest
from app import app

class FlaskAppTests(unittest.TestCase):
    "Test Application"
    # Set up the test client before each test
    def setUp(self):
        self.client = app.test_client()  # Flask test client

    def test_index_route(self):
        """Test the index route ('/')"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)  # Expect a 200 OK status
        self.assertIn(b"Select an Application", response.data)

    def test_select_app_route(self):
        """Test the select-app route ('/select-app')"""
        # Simulate a POST request with an application selection
        data = {'application': 'my_app'}
        response = self.client.post('/select-app', data=data)

        self.assertEqual(response.status_code, 302)  # Expect a redirect
        self.assertIn('/', response.headers['Location'])  # Check redirect location

    def test_select_app_route_no_app(self):
        """Test the select-app route with no application selected"""
        # Simulate a POST request without selecting an application
        data = {'application': ''}
        response = self.client.post('/select-app', data=data)

        self.assertEqual(response.status_code, 302)  # Expect a redirect back to index
        self.assertIn('/', response.headers['Location'])  # Check redirect location

    def test_close_session_route(self):
        """Test the close-session route ('/close-session')"""
        # Assume we have a session with ID '12345' for testing
        data = {'session_id': '12345'}
        response = self.client.post('/close-session', data=data)

        self.assertEqual(response.status_code, 302)  # Expect a redirect
        self.assertIn('/', response.headers['Location'])  # Check redirect location

    def test_invalid_session_video_feed(self):
        """Test invalid session for video feed ('/video_feed/<session_id>')"""
        session_id = 'invalid_session_id'
        response = self.client.get(f'/video_feed/{session_id}')

        self.assertEqual(response.status_code, 404)  # Expect 404 for invalid session
        self.assertIn(b"Invalid session", response.data)  # Check error message in response

    def test_invalid_session_stream_page(self):
        """Test invalid session for stream page ('/stream/<session_id>')"""
        session_id = 'invalid_session_id'
        response = self.client.get(f'/stream/{session_id}')

        self.assertEqual(response.status_code, 404)  # Expect 404 for invalid session
        self.assertIn(b"Session expired or invalid", response.data)

if __name__ == '__main__':
    unittest.main()
