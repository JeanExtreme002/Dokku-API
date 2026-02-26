import requests

from ..helpers import expect_json, expect_status, expect_true, require, step


def search_and_admin_resources(ctx):
    step("Searching resources")
    response = requests.post(
        ctx.base_url + "/api/search",
        params={"api_key": ctx.api_key, "q": ctx.user_app},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Search resources")
    expect_status(response, 200, "Search resources")
    expect_true(response_json.get("success"), "Search resources success")
    require(
        isinstance(response_json.get("result"), dict),
        "Search resources: expected result to be a dict",
    )

    step("Listing resources (admin)")
    response = requests.post(
        ctx.base_url + "/api/admin/resources/apps",
        headers={"MASTER-KEY": ctx.master_key},
    )
    expect_status(response, 200, "Admin resources apps")

    response = requests.post(
        ctx.base_url + "/api/admin/resources/services",
        headers={"MASTER-KEY": ctx.master_key},
    )
    expect_status(response, 200, "Admin resources services")

    response = requests.post(
        ctx.base_url + "/api/admin/resources/networks",
        headers={"MASTER-KEY": ctx.master_key},
    )
    expect_status(response, 200, "Admin resources networks")

    step("Listing plugins (admin)")
    response = requests.post(
        ctx.base_url + "/api/admin/plugins/list",
        headers={"MASTER-KEY": ctx.master_key},
    )
    response_json = expect_json(response, "Admin plugins list")
    expect_status(response, 200, "Admin plugins list")
    expect_true(response_json.get("success"), "Admin plugins list success")
