def require(condition, message):
    if not condition:
        raise AssertionError(message)


def describe_response(response):
    body = response.text
    if len(body) > 500:
        body = body[:500] + "... (truncated)"
    return f"status={response.status_code}, body={body}"


def expect_status(response, expected, label):
    if response.status_code != expected:
        raise AssertionError(
            f"{label}: expected status {expected}, got {describe_response(response)}"
        )


def expect_json(response, label):
    try:
        return response.json()
    except ValueError as exc:
        raise AssertionError(
            f"{label}: expected JSON response, got {describe_response(response)}"
        ) from exc


def expect_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def expect_true(value, label):
    if value is not True:
        raise AssertionError(f"{label}: expected True, got {value}")


def step(message):
    print(f"Test: {message}...")
