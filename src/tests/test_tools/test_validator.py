import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException, Request
from starlette.datastructures import State

from src.api.tools.validator import (
    UserCredentialsPayload,
    validate_admin,
    validate_api_key,
    validate_email_format,
    validate_user_credentials,
)

MOCK_MASTER_KEY = "master-abc123456789"
MOCK_API_KEY = "api-abc123456789"


class TestValidators(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock(spec=Request)
        self.mock_request.state = State()

    def test_validate_admin_with_admin_user(self):
        self.mock_request.state.session_user = MagicMock(is_admin=True)
        payload = UserCredentialsPayload(access_token="token")

        validate_admin(self.mock_request, master_key_header=None, payload=payload)

    def test_validate_admin_with_non_admin_user(self):
        self.mock_request.state.session_user = MagicMock(is_admin=False)
        payload = UserCredentialsPayload(access_token="token")

        with self.assertRaises(HTTPException) as ctx:
            validate_admin(self.mock_request, master_key_header=None, payload=payload)

        self.assertEqual(ctx.exception.status_code, 403)

    @patch("src.api.tools.validator.MASTER_KEY", MOCK_MASTER_KEY)
    def test_validate_admin_with_valid_master_key(self):
        self.mock_request.state.session_user = None

        validate_admin(
            self.mock_request, master_key_header=MOCK_MASTER_KEY, payload=None
        )

    @patch("src.api.tools.validator.MASTER_KEY", MOCK_MASTER_KEY)
    def test_validate_admin_with_invalid_master_key(self):
        self.mock_request.state.session_user = None

        with self.assertRaises(HTTPException) as ctx:
            validate_admin(self.mock_request, master_key_header="invalid", payload=None)

        self.assertEqual(ctx.exception.status_code, 401)

    @patch("src.api.tools.validator.MASTER_KEY", MOCK_MASTER_KEY)
    @patch("src.api.tools.validator.API_KEY", MOCK_API_KEY)
    def test_validate_api_key_valid(self):
        validate_api_key(MOCK_API_KEY)
        validate_api_key(MOCK_MASTER_KEY)

    @patch("src.api.tools.validator.API_KEY", MOCK_API_KEY)
    def test_validate_api_key_invalid(self):
        with self.assertRaises(HTTPException) as ctx:
            validate_api_key("wrong-key")

        self.assertEqual(ctx.exception.status_code, 401)

    def test_validate_user_credentials_valid(self):
        self.mock_request.state.session_user = MagicMock()
        payload = UserCredentialsPayload(access_token="token")

        validate_user_credentials(self.mock_request, payload)

    def test_validate_user_credentials_invalid(self):
        self.mock_request.state.session_user = None

        payload = UserCredentialsPayload(access_token="")

        with self.assertRaises(HTTPException) as ctx:
            validate_user_credentials(self.mock_request, payload)

        self.assertEqual(ctx.exception.status_code, 401)

    def test_validate_email_format_valid(self):
        validate_email_format("user@example.com")

    def test_validate_email_format_invalid_format(self):
        with self.assertRaises(HTTPException) as ctx:
            validate_email_format("invalid-email")

        self.assertEqual(ctx.exception.detail, "Invalid email format")

    def test_validate_email_format_too_long(self):
        long_email = "a" * 100 + "@example.com"

        with self.assertRaises(HTTPException) as ctx:
            validate_email_format(long_email)

        self.assertEqual(ctx.exception.detail, "Email is too long")
