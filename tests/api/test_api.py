"""API tests (pytest + requests). Mirrors the Postman collection."""
import pytest


@pytest.mark.api
@pytest.mark.smoke
def test_health_endpoint_returns_ok(api):
    r = api.health()
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.api
@pytest.mark.smoke
def test_login_success_returns_token(api, test_data):
    u = test_data["users"]["student"]
    r = api.login(u["username"], u["password"])
    assert r.status_code == 200
    body = r.json()
    assert body["token"]
    assert body["user"]["username"] == u["username"]


@pytest.mark.api
@pytest.mark.regression
def test_login_with_wrong_password_returns_401(api, test_data):
    u = test_data["users"]["student"]
    assert api.login(u["username"], "bad-password").status_code == 401


@pytest.mark.api
@pytest.mark.regression
def test_login_with_missing_fields_returns_400(api):
    assert api.login("", "").status_code == 400


@pytest.mark.api
@pytest.mark.regression
def test_login_locked_account_returns_423(api, test_data):
    u = test_data["users"]["locked"]
    assert api.login(u["username"], u["password"]).status_code == 423


@pytest.mark.api
@pytest.mark.regression
def test_courses_requires_authentication(api):
    assert api.list_courses(auth=False).status_code == 401


@pytest.mark.api
@pytest.mark.regression
def test_list_courses_returns_catalog(authed_api, test_data):
    r = authed_api.list_courses()
    assert r.status_code == 200
    ids = {c["id"] for c in r.json()["courses"]}
    assert {c["id"] for c in test_data["courses"].values()} <= ids


@pytest.mark.api
@pytest.mark.smoke
def test_enroll_in_course_returns_201(authed_api, test_data):
    cid = test_data["courses"]["python"]["id"]
    assert authed_api.enroll(cid).status_code == 201
    assert cid in authed_api.enrollments().json()["enrollments"]


@pytest.mark.api
@pytest.mark.regression
def test_duplicate_enrollment_returns_409(authed_api, test_data):
    cid = test_data["courses"]["python"]["id"]
    authed_api.enroll(cid)
    assert authed_api.enroll(cid).status_code == 409


@pytest.mark.api
@pytest.mark.regression
def test_enroll_in_full_course_returns_409(authed_api, test_data):
    r = authed_api.enroll(test_data["courses"]["full"]["id"])
    assert r.status_code == 409
    assert "full" in r.json()["error"].lower()


@pytest.mark.api
@pytest.mark.regression
def test_enroll_in_unknown_course_returns_404(authed_api):
    assert authed_api.enroll("C999").status_code == 404


@pytest.mark.api
@pytest.mark.smoke
def test_submit_assignment_returns_201(authed_api, test_data):
    authed_api.enroll(test_data["courses"]["python"]["id"])
    r = authed_api.submit_assignment(test_data["assignments"]["python_basics"]["id"], test_data["submission_text"])
    assert r.status_code == 201
    assert r.json()["submission"]["attempt"] == 1


@pytest.mark.api
@pytest.mark.regression
def test_submit_assignment_when_not_enrolled_returns_403(authed_api, test_data):
    r = authed_api.submit_assignment(test_data["assignments"]["python_basics"]["id"], "text")
    assert r.status_code == 403


@pytest.mark.api
@pytest.mark.regression
def test_submit_empty_assignment_returns_400(authed_api, test_data):
    authed_api.enroll(test_data["courses"]["python"]["id"])
    r = authed_api.submit_assignment(test_data["assignments"]["python_basics"]["id"], "   ")
    assert r.status_code == 400


@pytest.mark.api
@pytest.mark.regression
def test_submit_past_due_assignment_returns_422(authed_api, test_data):
    authed_api.enroll(test_data["courses"]["python"]["id"])
    r = authed_api.submit_assignment(test_data["assignments"]["past_due"]["id"], "late")
    assert r.status_code == 422
