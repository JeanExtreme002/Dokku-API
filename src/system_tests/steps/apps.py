import requests

from ..helpers import (
    expect_equal,
    expect_json,
    expect_status,
    expect_true,
    require,
    step,
)


def app_lifecycle(ctx):
    step("Creating a new app")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Create app")
    expect_status(response, 201, "Create app")
    expect_true(response_json.get("success"), "Create app success")

    step("Checking app exists")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/exists",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App exists")
    expect_status(response, 200, "App exists")
    expect_true(response_json.get("success"), "App exists success")

    step("Listing apps")
    response = requests.post(
        ctx.base_url + "/api/apps/list",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "List apps")
    expect_status(response, 200, "List apps")
    expect_true(response_json.get("success"), "List apps success")
    require(
        any(
            app_name.endswith(ctx.user_app)
            for app_name in response_json.get("result", {}).keys()
        ),
        "List apps: expected app name in result",
    )


def app_sharing(ctx):
    step("Listing shared apps (owner)")
    response = requests.post(
        ctx.base_url + "/api/apps/list-shared-apps",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "List shared apps (owner)")
    expect_status(response, 200, "List shared apps (owner)")
    expect_true(response_json.get("success"), "List shared apps (owner) success")
    expect_equal(response_json.get("result"), {}, "List shared apps (owner) result")

    step("Sharing app with second user")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/share/{ctx.user_email_2}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Share app")
    expect_status(response, 200, "Share app")
    expect_true(response_json.get("success"), "Share app success")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/sharing",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Sharing list")
    expect_status(response, 200, "Sharing list")
    expect_true(response_json.get("success"), "Sharing list success")
    require(
        ctx.user_email_2 in response_json.get("result", []),
        "Sharing list: expected secondary user",
    )

    response = requests.post(
        ctx.base_url + "/api/apps/list-shared-apps",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token_2},
    )
    response_json = expect_json(response, "List shared apps (secondary)")
    expect_status(response, 200, "List shared apps (secondary)")
    expect_true(
        response_json.get("success"),
        "List shared apps (secondary) success",
    )
    require(
        any(
            key.startswith(ctx.user_email) and key.endswith(ctx.user_app)
            for key in response_json.get("result", {}).keys()
        ),
        "List shared apps (secondary): expected shared app entry",
    )

    step("Unsharing app from second user")
    response = requests.delete(
        ctx.base_url + f"/api/apps/{ctx.user_app}/share/{ctx.user_email_2}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Unshare app")
    expect_status(response, 200, "Unshare app")
    expect_true(response_json.get("success"), "Unshare app success")

    response = requests.post(
        ctx.base_url + "/api/apps/list-shared-apps",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token_2},
    )
    response_json = expect_json(response, "List shared apps (after unshare)")
    expect_status(response, 200, "List shared apps (after unshare)")
    expect_true(
        response_json.get("success"),
        "List shared apps (after unshare) success",
    )
    expect_equal(
        response_json.get("result"),
        {},
        "List shared apps (after unshare) result",
    )


def quota_and_app_info(ctx):
    step("Must not exceed quota when creating a new app")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app + 'new'}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Create app beyond quota")
    expect_status(response, 403, "Create app beyond quota")
    expect_equal(response_json, {"detail": "Quota exceeded"}, "App quota error")

    step("Getting app information")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/info",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App info")
    expect_status(response, 200, "App info")
    expect_true(response_json.get("success"), "App info success")
    expect_equal(
        response_json.get("result", {}).get("data", {}).get("deployed"),
        "false",
        "App info deployed",
    )

    step("Getting app URL")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/url",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App URL")
    expect_status(response, 200, "App URL")
    expect_true(response_json.get("success"), "App URL success")

    step("Getting app logs")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/logs",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    expect_status(response, 200, "App logs")

    step("Getting app deployment token")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/deployment-token",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App deployment token")
    expect_status(response, 200, "App deployment token")
    expect_true(response_json.get("success"), "App deployment token success")
    require(
        len(response_json.get("result", "")) > 0,
        "App deployment token: expected non-empty token",
    )


def app_config(ctx):
    step("Setting app configuration")
    response = requests.post(
        ctx.base_url + f"/api/config/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Config list initial")
    expect_status(response, 200, "Config list initial")
    expect_true(response_json.get("success"), "Config list initial success")
    expect_equal(response_json.get("result"), {}, "Config list initial result")

    response = requests.put(
        ctx.base_url + f"/api/config/{ctx.user_app}/{ctx.user_app_key}",
        params={"api_key": ctx.api_key, "value": ctx.user_app_key_value},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Config set")
    expect_status(response, 200, "Config set")
    expect_true(response_json.get("success"), "Config set success")

    response = requests.post(
        ctx.base_url + f"/api/config/{ctx.user_app}/{ctx.user_app_key}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Config get single")
    expect_status(response, 200, "Config get single")
    expect_true(response_json.get("success"), "Config get single success")
    expect_equal(
        response_json.get("result"),
        ctx.user_app_key_value,
        "Config get single value",
    )

    response = requests.post(
        ctx.base_url + f"/api/config/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Config list")
    expect_status(response, 200, "Config list")
    expect_true(response_json.get("success"), "Config list success")
    expect_equal(
        response_json.get("result"),
        {ctx.user_app_key: ctx.user_app_key_value},
        "Config list value",
    )

    response = requests.delete(
        ctx.base_url + f"/api/config/{ctx.user_app}/{ctx.user_app_key}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Config delete")
    expect_status(response, 200, "Config delete")
    expect_true(response_json.get("success"), "Config delete success")

    response = requests.post(
        ctx.base_url + f"/api/config/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Config list empty")
    expect_status(response, 200, "Config list empty")
    expect_true(response_json.get("success"), "Config list empty success")
    expect_equal(response_json.get("result"), {}, "Config list empty result")


def deploy_and_builder(ctx):
    step("Deploying application")
    response = requests.put(
        ctx.base_url + f"/api/deploy/{ctx.user_app}",
        params={"api_key": ctx.api_key, "repo_url": ctx.user_app_repo_url},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Deploy app")
    expect_status(response, 200, "Deploy app")
    expect_true(response_json.get("success"), "Deploy app success")

    step("Getting deployment info")
    response = requests.post(
        ctx.base_url + f"/api/deploy/{ctx.user_app}/info",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Deployment info")
    expect_status(response, 200, "Deployment info")
    expect_true(response_json.get("success"), "Deployment info success")

    step("Getting builder info")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/builder",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Builder info")
    expect_status(response, 200, "Builder info")
    expect_true(response_json.get("success"), "Builder info success")

    step("Setting builder")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/builder/dockerfile",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Set builder")
    expect_status(response, 200, "Set builder")
    expect_true(response_json.get("success"), "Set builder success")


def domains_and_ports(ctx):
    step("Setting domain for the app")
    response = requests.post(
        ctx.base_url + f"/api/domains/{ctx.user_app}/{ctx.user_app_domain}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Set domain")
    expect_status(response, 200, "Set domain")
    expect_true(response_json.get("success"), "Set domain success")

    step("Getting domains info")
    response = requests.post(
        ctx.base_url + f"/api/domains/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Get domains")
    expect_status(response, 200, "Get domains")
    expect_true(response_json.get("success"), "Get domains success")

    step("Unsetting domain for the app")
    response = requests.delete(
        ctx.base_url + f"/api/domains/{ctx.user_app}/{ctx.user_app_domain}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Delete domain")
    expect_status(response, 200, "Delete domain")
    expect_true(response_json.get("success"), "Delete domain success")

    step("Setting port mapping for the app")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/ports",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Ports list initial")
    expect_status(response, 200, "Ports list initial")
    expect_true(response_json.get("success"), "Ports list initial success")
    expect_equal(response_json.get("result"), [], "Ports list initial result")

    response = requests.post(
        ctx.base_url
        + f"/api/apps/{ctx.user_app}/ports/{ctx.user_app_port_mapping['protocol']}/{ctx.user_app_port_mapping['origin']}/{ctx.user_app_port_mapping['dest']}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    expect_status(response, 200, "Add port mapping")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/ports",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Ports list after add")
    expect_status(response, 200, "Ports list after add")
    expect_true(response_json.get("success"), "Ports list after add success")
    expect_equal(
        response_json.get("result"),
        [ctx.user_app_port_mapping],
        "Ports list after add result",
    )

    step("Unsetting port mapping for the app")
    response = requests.delete(
        ctx.base_url
        + f"/api/apps/{ctx.user_app}/ports/{ctx.user_app_port_mapping['protocol']}/{ctx.user_app_port_mapping['origin']}/{ctx.user_app_port_mapping['dest']}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    expect_status(response, 200, "Delete port mapping")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/ports",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Ports list after delete")
    expect_status(response, 200, "Ports list after delete")
    expect_equal(response_json.get("result"), [], "Ports list after delete result")
