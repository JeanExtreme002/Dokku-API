import secrets
import time
from dataclasses import dataclass


@dataclass
class TestContext:
    base_url: str
    master_key: str
    api_key: str
    test_id: str
    user_email: str
    user_token: str
    user_app: str
    user_app_domain: str
    user_app_repo_url: str
    user_app_key: str
    user_app_key_value: str
    user_app_port_mapping: dict
    user_database: str
    user_network: str
    user_app_renamed: str
    user_app_domain_2: str
    user_email_2: str
    user_token_2: str
    user_email_2_updated: str


def build_context(base_url, master_key, api_key):
    test_id = str(time.time()).replace(".", "")
    user_app = "test-app"
    return TestContext(
        base_url=base_url,
        master_key=master_key,
        api_key=api_key,
        test_id=test_id,
        user_email=f"test{test_id}@example.com",
        user_token=secrets.token_urlsafe(256),
        user_app=user_app,
        user_app_domain="testdokkuapi.com",
        user_app_repo_url="https://github.com/heroku/ruby-getting-started",
        user_app_key=f"key{secrets.token_hex(8)}",
        user_app_key_value=secrets.token_hex(8),
        user_app_port_mapping={"protocol": "http", "origin": 5300, "dest": 7040},
        user_database="test_database",
        user_network="test_network",
        user_app_renamed=f"{user_app}-renamed",
        user_app_domain_2=f"alt{test_id}.example.com",
        user_email_2=f"test{test_id}_2@example.com",
        user_token_2=secrets.token_urlsafe(256),
        user_email_2_updated=f"test{test_id}_2_updated@example.com",
    )
