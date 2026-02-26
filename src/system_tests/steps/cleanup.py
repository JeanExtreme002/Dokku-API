import requests

from ..helpers import expect_equal, expect_json, expect_status, expect_true, step


def unlink_and_cleanup(ctx):
    step("Unlinking app from network")
    response = requests.delete(
        ctx.base_url + f"/api/networks/{ctx.user_network}/link/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Unlink app from network")
    expect_status(response, 200, "Unlink app from network")
    expect_true(response_json.get("success"), "Unlink app from network success")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/network",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App network after unlink")
    expect_status(response, 200, "App network after unlink")
    expect_true(response_json.get("success"), "App network after unlink success")
    expect_equal(
        response_json.get("result"),
        {"network": None},
        "App network after unlink result",
    )

    step("Unlinking app from database")
    response = requests.delete(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/link/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Unlink app from database")
    expect_status(response, 200, "Unlink app from database")
    expect_true(response_json.get("success"), "Unlink app from database success")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/databases",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App databases after unlink")
    expect_status(response, 200, "App databases after unlink")
    expect_true(response_json.get("success"), "App databases after unlink success")
    expect_equal(
        response_json.get("result"),
        {},
        "App databases after unlink result",
    )

    step("Deleting network")
    response = requests.delete(
        ctx.base_url + f"/api/networks/{ctx.user_network}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Delete network")
    expect_status(response, 200, "Delete network")
    expect_true(response_json.get("success"), "Delete network success")

    step("Deleting database")
    response = requests.delete(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Delete database")
    expect_status(response, 200, "Delete database")
    expect_true(response_json.get("success"), "Delete database success")

    step("Deleting app")
    response = requests.delete(
        ctx.base_url + f"/api/apps/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Delete app")
    expect_status(response, 200, "Delete app")
    expect_true(response_json.get("success"), "Delete app success")
