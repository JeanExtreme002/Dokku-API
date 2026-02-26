import os
import sys

from .context import build_context
from .steps.admin import admin_user_management, admin_user_setup, credential_checks
from .steps.apps import (
    app_config,
    app_lifecycle,
    app_sharing,
    deploy_and_builder,
    domains_and_ports,
    quota_and_app_info,
)
from .steps.base import check_base_endpoints
from .steps.cleanup import unlink_and_cleanup
from .steps.databases import database_lifecycle, database_linking
from .steps.misc import search_and_admin_resources
from .steps.networks import network_lifecycle, network_linking


def main():
    if len(sys.argv) != 4:
        print(sys.argv)
        raise ValueError("Usage: python test_app.py <base_url> <master_key> <api_key>")

    base_url = sys.argv[1]
    master_key = sys.argv[2]
    api_key = sys.argv[3]

    print(
        f"Testing API at {base_url} with MASTER_KEY={master_key} and API_KEY={api_key}"
    )

    ctx = build_context(base_url, master_key, api_key)

    _ = os.getenv("RUN_LETSENCRYPT_TESTS", "0") == "1"
    _ = os.getenv("RUN_PLUGIN_TESTS", "0") == "1"
    _ = os.getenv("RUN_SSH_TESTS", "0") == "1"
    _ = os.getenv("RUN_UPLOAD_TESTS", "0") == "1"
    _ = os.getenv("RUN_ADMIN_DANGEROUS_TESTS", "0") == "1"
    _ = os.getenv("RUN_ADMIN_STORAGE_TESTS", "0") == "1"

    check_base_endpoints(ctx)
    admin_user_setup(ctx)
    credential_checks(ctx)
    admin_user_management(ctx)
    app_lifecycle(ctx)
    app_sharing(ctx)
    quota_and_app_info(ctx)
    app_config(ctx)
    database_lifecycle(ctx)
    database_linking(ctx)
    network_lifecycle(ctx)
    network_linking(ctx)
    search_and_admin_resources(ctx)
    deploy_and_builder(ctx)
    domains_and_ports(ctx)
    unlink_and_cleanup(ctx)

    print("All tests passed successfully!")


if __name__ == "__main__":
    main()
