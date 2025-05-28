from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from src.api.app import get_app

app = get_app()
client = TestClient(app)


class TestFastAPI(IsolatedAsyncioTestCase):

    def test_api_health(self):
        """
        Test if server is alive.
        """
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
