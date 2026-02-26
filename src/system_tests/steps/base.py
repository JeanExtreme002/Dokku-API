import requests

from ..helpers import expect_equal, expect_json, expect_status, expect_true, step


def check_base_endpoints(ctx):
    step("Checking base endpoints")
    response = requests.get(ctx.base_url)
    expect_status(response, 200, "Base URL")

    response = requests.get(ctx.base_url + "/api")
    response_json = expect_json(response, "API status")
    expect_status(response, 200, "API status")
    expect_true(response_json.get("dokku_status"), "API status dokku_status")

    response = requests.get(ctx.base_url + "/api/list-databases")
    response_json = expect_json(response, "List databases")
    expect_status(response, 200, "List databases")
    expect_equal(
        response_json.get("result"),
        [
            "postgres",
            "mysql",
            "mongodb",
            "redis",
            "mariadb",
            "couchdb",
            "cassandra",
            "elasticsearch",
            "influxdb",
        ],
        "List databases result",
    )
