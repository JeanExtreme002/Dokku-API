import unittest
from unittest.mock import patch

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.api.middlewares.session import SessionUserMiddleware


class TestSessionUserMiddleware(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()

        @self.app.post("/test-endpoint")
        async def test_endpoint(request: Request):
            user = request.state.session_user
            return {"user": user.email if user else None}

        self.app.add_middleware(SessionUserMiddleware)
        self.client = TestClient(self.app)

    @patch("src.api.middlewares.session.get_user_by_access_token")
    def test_valid_access_token_sets_session_user(self, mock_get_user):
        mock_user = type("User", (), {"email": "test@example.com"})
        mock_get_user.return_value = mock_user

        response = self.client.post(
            "/test-endpoint", json={"access_token": "validtoken"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"], "test@example.com")
        mock_get_user.assert_awaited_once_with("validtoken")

    @patch("src.api.middlewares.session.get_user_by_access_token")
    def test_invalid_access_token_returns_401(self, mock_get_user):
        from fastapi import HTTPException

        mock_get_user.side_effect = HTTPException(
            status_code=401, detail="Invalid token"
        )

        response = self.client.post(
            "/test-endpoint", json={"access_token": "invalidtoken"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid token"})

    def test_invalid_json_body_does_not_crash(self):
        headers = {"Content-Type": "application/json"}
        response = self.client.post("/test-endpoint", data="not json", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"user": None})

    def test_non_json_request_passes_through(self):
        headers = {"Content-Type": "text/plain"}
        response = self.client.post(
            "/test-endpoint", data="plain text", headers=headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"user": None})
