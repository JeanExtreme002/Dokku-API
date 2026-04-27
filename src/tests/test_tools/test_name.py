import unittest
from unittest.mock import patch

from src.api.models import App, Service
from src.api.schemas import UserSchema
from src.api.tools.resource import ResourceName

MockUser = UserSchema(
    id=1,
    email="john.doe@example.com",
    access_token="token",
    is_admin=False,
    created_at="2023-01-01T00:00:00Z",
    apps_quota=1,
    services_quota=1,
    networks_quota=1,
)


@patch("src.api.tools.resource.Config.API_USE_PER_USER_RESOURCE_NAMES", True)
class TestResourceName(unittest.TestCase):
    def test_normalization_for_app(self):
        name = "My Resource!Name"
        rname = ResourceName(user=MockUser, name=name)
        self.assertEqual(rname.normalized(), "my-resource-name")
        self.assertEqual(str(rname), "my-resource-name")
        self.assertEqual(rname.for_system(), "1-my-resource-name")

    def test_normalization_for_service(self):
        name = "My Resource!Name"
        rname = ResourceName(user=MockUser, name=name)
        self.assertEqual(rname.normalized(), "my-resource-name")
        self.assertEqual(str(rname), "my-resource-name")
        self.assertEqual(rname.for_system(), "1-my-resource-name")

    def test_decoding_app_name(self):
        name = "1-my-resource-name"
        rname = ResourceName(user=MockUser, name=name, from_system=True)
        self.assertEqual(rname.normalized(), "my-resource-name")
        self.assertEqual(str(rname), "my-resource-name")
        self.assertEqual(rname.for_system(), "1-my-resource-name")

    def test_decoding_service_name(self):
        name = "1-my-resource-name"
        rname = ResourceName(user=MockUser, name=name, from_system=True)
        self.assertEqual(rname.normalized(), "my-resource-name")
        self.assertEqual(str(rname), "my-resource-name")
        self.assertEqual(rname.for_system(), "1-my-resource-name")
