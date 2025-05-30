# tests/test_rate_limit.py

import unittest

import httpx
from fastapi import FastAPI

from src.api.middleware import RateLimiterMiddleware


class TestRateLimiting(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = FastAPI()
        self.app.add_middleware(RateLimiterMiddleware(self.app))

        @self.app.get("/")
        async def test_endpoint():
            pass

        transport = httpx.ASGITransport(app=self.app)
        self.client = httpx.AsyncClient(transport=transport, base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_rate_limit_within_limit(self):
        for i in range(10):
            response = await self.client.get("/")
            self.assertEqual(response.status_code, 200, msg=f"Failed at request {i+1}")

    async def test_global_rate_limit_exceeded(self):
        for i in range(2000):
            response = await self.client.get("/")

        response = await self.client.get("/")
        self.assertEqual(response.status_code, 429)
        self.assertIn("rate limit", response.text.lower())
