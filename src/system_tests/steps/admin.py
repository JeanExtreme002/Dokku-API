import requests

from ..helpers import (
    describe_response,
    expect_equal,
    expect_json,
    expect_status,
    require,
    step,
)


def admin_user_setup(ctx):
    step("Creating a new user")
    response = requests.post(
        ctx.base_url
        + f"/api/admin/users/{ctx.user_email}?access_token={ctx.user_token}",
        headers={"MASTER-KEY": ctx.master_key, "Content-Type": "application/json"},
    )
    expect_status(response, 201, "Create user")

    step("Must not create with an existing email")
    response = requests.post(
        ctx.base_url + f"/api/admin/users/{ctx.user_email}",
        params={"access_token": ctx.user_token + "new"},
        headers={"MASTER-KEY": ctx.master_key, "Content-Type": "application/json"},
    )
    require(
        response.status_code != 201,
        "Create user with existing email should fail: " + describe_response(response),
    )

    step("Must not create with an existing token")
    response = requests.post(
        ctx.base_url + f"/api/admin/users/{ctx.user_email + 'new'}",
        params={"access_token": ctx.user_token},
        headers={"MASTER-KEY": ctx.master_key, "Content-Type": "application/json"},
    )
    require(
        response.status_code != 201,
        "Create user with existing token should fail: " + describe_response(response),
    )

    step("Creating a new user again (double-check)")
    response = requests.post(
        ctx.base_url + f"/api/admin/users/{ctx.user_email + 'new'}",
        params={"access_token": ctx.user_token + "new"},
        headers={"MASTER-KEY": ctx.master_key},
    )
    expect_status(response, 201, "Create user again")

    step("Creating a second user")
    response = requests.post(
        ctx.base_url + f"/api/admin/users/{ctx.user_email_2}",
        params={"access_token": ctx.user_token_2},
        headers={"MASTER-KEY": ctx.master_key},
    )
    expect_status(response, 201, "Create second user")


def credential_checks(ctx):
    step("Checking user credentials")
    response = requests.post(
        ctx.base_url + "/api/apps/list",
        params={"api_key": "invalid"},
        json={"access_token": ctx.user_token},
    )
    expect_status(response, 401, "Invalid api_key")

    response = requests.post(
        ctx.base_url + "/api/apps/list",
        params={"api_key": ctx.api_key},
        json={"access_token": "invalid"},
    )
    expect_status(response, 401, "Invalid access_token")

    response = requests.post(
        ctx.base_url + "/api/quota",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Quota")
    expect_status(response, 200, "Quota")
    expect_equal(
        response_json,
        {"apps_quota": 0, "services_quota": 0, "networks_quota": 0},
        "Initial quota",
    )

    step("Checking admin credentials")
    response = requests.post(
        ctx.base_url + "/api/admin/users/list",
        headers={"MASTER-KEY": "invalid_key"},
    )
    expect_status(response, 401, "Invalid master key")


def admin_user_management(ctx):
    step("Listing users (admin)")
    response = requests.post(
        ctx.base_url + "/api/admin/users/list",
        headers={"MASTER-KEY": ctx.master_key},
    )
    response_json = expect_json(response, "List users")
    expect_status(response, 200, "List users")
    require(
        isinstance(response_json, list),
        f"List users: expected list, got {type(response_json).__name__}",
    )

    step("Taking over user (admin)")
    response = requests.post(
        ctx.base_url + f"/api/admin/users/{ctx.user_email}/take-over",
        headers={"MASTER-KEY": ctx.master_key},
    )
    response_json = expect_json(response, "Take over user")
    expect_status(response, 200, "Take over user")
    require("access_token" in response_json, "Take over user: access_token missing")

    step("Increasing user quota")
    response = requests.put(
        ctx.base_url + f"/api/admin/users/{ctx.user_email}/quota",
        params={
            "apps_quota": 1,
            "services_quota": 1,
            "networks_quota": 1,
        },
        headers={"MASTER-KEY": ctx.master_key},
    )
    expect_status(response, 200, "Increase quota")

    response = requests.post(
        ctx.base_url + "/api/quota",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Quota after update")
    expect_status(response, 200, "Quota after update")
    expect_equal(
        response_json,
        {"apps_quota": 1, "services_quota": 1, "networks_quota": 1},
        "Quota after update",
    )
