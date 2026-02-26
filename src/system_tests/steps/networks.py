import requests

from ..helpers import (
    expect_equal,
    expect_json,
    expect_status,
    expect_true,
    require,
    step,
)


def network_lifecycle(ctx):
    step("Creating a new network")
    response = requests.post(
        ctx.base_url + f"/api/networks/{ctx.user_network}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Create network")
    expect_status(response, 201, "Create network")
    expect_true(response_json.get("success"), "Create network success")

    step("Listing networks")
    response = requests.post(
        ctx.base_url + "/api/networks/list",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "List networks")
    expect_status(response, 200, "List networks")
    expect_true(response_json.get("success"), "List networks success")
    require(
        ctx.user_network in response_json.get("result", []),
        "List networks: expected network in list",
    )

    step("Checking used quota")
    response = requests.post(
        ctx.base_url + "/api/quota/used",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Used quota")
    expect_status(response, 200, "Used quota")
    expect_equal(
        response_json,
        {"apps_used": 1, "services_used": 1, "networks_used": 1},
        "Used quota",
    )

    step("Must not exceed quota when creating a new network")
    response = requests.post(
        ctx.base_url + f"/api/networks/{ctx.user_network + 'new'}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Create network beyond quota")
    expect_status(response, 403, "Create network beyond quota")
    expect_equal(
        response_json,
        {"detail": "Quota exceeded"},
        "Network quota error",
    )


def network_linking(ctx):
    step("Linking app to network")
    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/network",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App network info")
    expect_status(response, 200, "App network info")
    expect_true(response_json.get("success"), "App network info success")
    expect_equal(
        response_json.get("result"),
        {"network": None},
        "App network info result",
    )

    response = requests.post(
        ctx.base_url + f"/api/networks/{ctx.user_network}/link/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Link network to app")
    expect_status(response, 200, "Link network to app")
    expect_true(response_json.get("success"), "Link network to app success")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/network",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App network info after link")
    expect_status(response, 200, "App network info after link")
    expect_true(response_json.get("success"), "App network info after link success")
    expect_equal(
        response_json.get("result"),
        {"network": ctx.user_network},
        "App network info after link result",
    )

    response = requests.post(
        ctx.base_url + f"/api/networks/{ctx.user_network}/linked-apps",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Network linked apps")
    expect_status(response, 200, "Network linked apps")
    expect_true(response_json.get("success"), "Network linked apps success")
    expect_equal(
        response_json.get("result"),
        [ctx.user_app],
        "Network linked apps result",
    )
