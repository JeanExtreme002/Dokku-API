import unittest

from src.api.models.models import App, Service
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName

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


class TestResourceName(unittest.TestCase):
    def test_normalization_for_app(self):
        name = "My Resource!Name"
        rname = ResourceName(user=MockUser, name=name, resource_type=App)
        self.assertEqual(rname.normalized(), "my-resource-name")
        self.assertEqual(str(rname), "my-resource-name")
        self.assertEqual(rname.for_system(), "1-my-resource-name")

    def test_normalization_for_service(self):
        name = "My Resource!Name"
        rname = ResourceName(user=MockUser, name=name, resource_type=Service)
        self.assertEqual(rname.normalized(), "my_resource_name")
        self.assertEqual(str(rname), "my_resource_name")
        self.assertEqual(rname.for_system(), "1_my_resource_name")

    def test_normalization_from_app(self):
        name = "1-my-resource-name"
        rname = ResourceName(
            user=MockUser, name=name, resource_type=App, from_system=True
        )
        self.assertEqual(rname.normalized(), "my-resource-name")
        self.assertEqual(str(rname), "my-resource-name")
        self.assertEqual(rname.for_system(), "1-my-resource-name")

    def test_normalization_from_service(self):
        name = "1_my_resource_name"
        rname = ResourceName(
            user=MockUser, name=name, resource_type=Service, from_system=True
        )
        self.assertEqual(rname.normalized(), "my_resource_name")
        self.assertEqual(str(rname), "my_resource_name")
        self.assertEqual(rname.for_system(), "1_my_resource_name")
