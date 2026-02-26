import requests

from ..helpers import (
    expect_equal,
    expect_json,
    expect_status,
    expect_true,
    require,
    step,
)


def database_lifecycle(ctx):
    step("Creating a new database")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Create database")
    expect_status(response, 201, "Create database")
    expect_true(response_json.get("success"), "Create database success")

    step("Listing databases")
    response = requests.post(
        ctx.base_url + "/api/databases/list",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "List databases")
    expect_status(response, 200, "List databases")
    expect_true(response_json.get("success"), "List databases success")
    require(
        ctx.user_database in response_json.get("result", {}).get("mysql", []),
        "List databases: expected database in mysql list",
    )

    response = requests.post(
        ctx.base_url + "/api/databases/mysql/list",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "List mysql databases")
    expect_status(response, 200, "List mysql databases")
    expect_true(response_json.get("success"), "List mysql databases success")
    require(
        ctx.user_database in response_json.get("result", []),
        "List mysql databases: expected database in list",
    )

    step("Getting database URI")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/uri",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database URI")
    expect_status(response, 200, "Database URI")
    expect_true(response_json.get("success"), "Database URI success")
    require(
        "mysql://" in response_json.get("result", ""),
        "Database URI: expected mysql://",
    )

    step("Must not exceed quota when creating a new database")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database + 'new'}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Create database beyond quota")
    expect_status(response, 403, "Create database beyond quota")
    expect_equal(
        response_json,
        {"detail": "Quota exceeded"},
        "Database quota error",
    )

    step("Getting database information")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/info",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database info")
    expect_status(response, 200, "Database info")
    expect_true(response_json.get("success"), "Database info success")
    expect_equal(
        response_json.get("result", {}).get("plugin_name"),
        "mysql",
        "Database plugin name",
    )

    step("Getting database logs")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/logs",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database logs")
    expect_status(response, 200, "Database logs")
    expect_true(response_json.get("success"), "Database logs success")

    step("Stopping database")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/stop",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database stop")
    expect_status(response, 200, "Database stop")
    expect_true(response_json.get("success"), "Database stop success")

    step("Starting database")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/start",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database start")
    expect_status(response, 200, "Database start")
    expect_true(response_json.get("success"), "Database start success")

    step("Restarting database")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/restart",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database restart")
    expect_status(response, 200, "Database restart")
    expect_true(response_json.get("success"), "Database restart success")


def database_linking(ctx):
    step("Linking app to database")
    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/linked-apps",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database linked apps")
    expect_status(response, 200, "Database linked apps")
    expect_equal(response_json.get("result"), [], "Database linked apps list")

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/databases",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App databases list")
    expect_status(response, 200, "App databases list")
    expect_true(response_json.get("success"), "App databases list success")
    expect_equal(response_json.get("result"), {}, "App databases list result")

    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/link/{ctx.user_app}",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Link database to app")
    expect_status(response, 200, "Link database to app")
    expect_true(response_json.get("success"), "Link database to app success")

    response = requests.post(
        ctx.base_url + f"/api/databases/mysql/{ctx.user_database}/linked-apps",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "Database linked apps after link")
    expect_status(response, 200, "Database linked apps after link")
    expect_equal(
        response_json.get("result"),
        [ctx.user_app],
        "Database linked apps after link result",
    )

    response = requests.post(
        ctx.base_url + f"/api/apps/{ctx.user_app}/databases",
        params={"api_key": ctx.api_key},
        json={"access_token": ctx.user_token},
    )
    response_json = expect_json(response, "App databases after link")
    expect_status(response, 200, "App databases after link")
    expect_true(response_json.get("success"), "App databases after link success")
    expect_equal(
        response_json.get("result"),
        {"mysql": [ctx.user_database]},
        "App databases after link result",
    )
