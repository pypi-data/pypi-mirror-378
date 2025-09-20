import re
from stdresponse import StandardResponse


def test_success_default():
    resp = StandardResponse.success()
    assert resp["success"] is True
    assert resp["status_code"] == 200
    assert resp["message"] == "Request successful."
    assert resp["data"] is None
    assert resp["error"] is None
    assert "timestamp" in resp["meta"]
    assert re.match(r".*Z$", resp["meta"]["timestamp"])
    assert "requestId" in resp["meta"]


def test_success_with_data_and_meta():
    resp = StandardResponse.success(
        data={"id": 1},
        message="User fetched.",
        meta={"ip": "127.0.0.1"}
    )
    assert resp["data"] == {"id": 1}
    assert resp["message"] == "User fetched."
    assert resp["meta"]["ip"] == "127.0.0.1"


def test_error_default():
    resp = StandardResponse.error()
    assert resp["success"] is False
    assert resp["status_code"] == 400
    assert resp["message"] == "An error occurred."
    assert resp["data"] is None
    assert resp["error"]["type"] == "GENERAL_ERROR"
    assert isinstance(resp["error"]["details"], list)
    assert "timestamp" in resp["meta"]
    assert "requestId" in resp["meta"]


def test_error_custom():
    resp = StandardResponse.error(
        message="Invalid input",
        status_code=422,
        error_type="VALIDATION_ERROR",
        error_details=[{"field": "email", "error": "Invalid format"}],
        meta={"service": "user-service"}
    )
    assert resp["message"] == "Invalid input"
    assert resp["status_code"] == 422
    assert resp["error"]["type"] == "VALIDATION_ERROR"
    assert resp["error"]["details"][0]["field"] == "email"
    assert resp["meta"]["service"] == "user-service"
