"""Regenerates postman/*.json (run: python scripts/build_postman_collection.py)."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "postman"
BASE = "{{baseUrl}}"


def req(name, method, path, tests, body=None, auth=True):
    r = {"method": method, "header": [], "url": {"raw": f"{BASE}{path}", "host": ["{{baseUrl}}"],
                                                 "path": path.strip("/").split("/")}}
    if body is not None:
        r["header"].append({"key": "Content-Type", "value": "application/json"})
        r["body"] = {"mode": "raw", "raw": json.dumps(body, indent=2)}
    if not auth:
        r["auth"] = {"type": "noauth"}
    return {"name": name, "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}],
            "request": r}


def status(code, *extra):
    return [f"pm.test('Status code is {code}', function () {{ pm.response.to.have.status({code}); }});", *extra]


def check(desc, expr):
    return f"pm.test('{desc}', function () {{ {expr} }});"


login_ok_tests = status(200,
    check("Response contains a token", "var j = pm.response.json(); pm.expect(j.token).to.be.a('string').and.not.empty; pm.collectionVariables.set('token', j.token);"),
    check("User name matches", "pm.expect(pm.response.json().user.username).to.eql(pm.collectionVariables.get('username'));"),
    check("Response time under 2000 ms", "pm.expect(pm.response.responseTime).to.be.below(2000);"))

folders = [
 ("00 Setup", [
   req("Reset test data (mock LMS only)", "POST", "/api/test/reset", status(200), auth=False)]),
 ("01 Health", [
   req("GET health", "GET", "/api/health", status(200,
       check("Status is ok", "pm.expect(pm.response.json().status).to.eql('ok');")), auth=False)]),
 ("02 Authentication", [
   req("POST login - valid credentials", "POST", "/api/auth/login", login_ok_tests,
       {"username": "{{username}}", "password": "{{password}}"}, auth=False),
   req("POST login - wrong password", "POST", "/api/auth/login", status(401,
       check("Error message present", "pm.expect(pm.response.json().error).to.be.a('string');")),
       {"username": "{{username}}", "password": "WrongPass!"}, auth=False),
   req("POST login - missing fields", "POST", "/api/auth/login", status(400), {"username": "", "password": ""}, auth=False),
   req("POST login - locked account", "POST", "/api/auth/login", status(423),
       {"username": "locked_user", "password": "Password123!"}, auth=False)]),
 ("03 Courses", [
   req("GET courses - no token", "GET", "/api/courses", status(401), auth=False),
   req("GET courses - authenticated", "GET", "/api/courses", status(200,
       check("Catalog contains C101, C102 and C103", "var ids = pm.response.json().courses.map(function (c) { return c.id; }); pm.expect(ids).to.include.members(['C101','C102','C103']);"),
       check("C103 is reported as full", "var c = pm.response.json().courses.filter(function (x) { return x.id === 'C103'; })[0]; pm.expect(c.full).to.be.true;")))]),
 ("04 Enrollment", [
   req("POST enroll - C101", "POST", "/api/courses/C101/enroll", status(201,
       check("Enrollment echoes course id", "pm.expect(pm.response.json().enrollment.course_id).to.eql('C101');"))),
   req("POST enroll - duplicate C101", "POST", "/api/courses/C101/enroll", status(409)),
   req("POST enroll - full course C103", "POST", "/api/courses/C103/enroll", status(409,
       check("Error mentions course is full", "pm.expect(pm.response.json().error.toLowerCase()).to.include('full');"))),
   req("POST enroll - unknown course", "POST", "/api/courses/C999/enroll", status(404)),
   req("GET my enrollments", "GET", "/api/enrollments", status(200,
       check("Contains C101 only", "pm.expect(pm.response.json().enrollments).to.eql(['C101']);")))]),
 ("05 Assignments", [
   req("POST submission - no token", "POST", "/api/assignments/A101/submissions", status(401),
       {"text": "answer"}, auth=False),
   req("POST submission - valid text", "POST", "/api/assignments/A101/submissions", status(201,
       check("Attempt number is 1", "pm.expect(pm.response.json().submission.attempt).to.eql(1);")),
       {"text": "This is my answer for the assignment."}),
   req("POST submission - empty text", "POST", "/api/assignments/A101/submissions", status(400), {"text": "   "}),
   req("POST submission - past due (A103)", "POST", "/api/assignments/A103/submissions", status(422), {"text": "late"}),
   req("POST submission - not enrolled (A102)", "POST", "/api/assignments/A102/submissions", status(403), {"text": "x"})]),
]

collection = {
    "info": {"name": "LMS API Tests", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
             "description": "Sample LMS API tests. Run in order (folders depend on the token saved by 'POST login - valid credentials'). "
                            "Folder 00 resets the bundled mock LMS; skip it against a real LMS."},
    "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}]},
    "variable": [{"key": "token", "value": ""}],
    "item": [{"name": n, "item": items} for n, items in folders],
}
environment = {
    "id": "lms-local-env", "name": "LMS Local", "_postman_variable_scope": "environment",
    "values": [{"key": "baseUrl", "value": "http://127.0.0.1:5000", "enabled": True},
               {"key": "username", "value": "student1", "enabled": True},
               {"key": "password", "value": "Password123!", "enabled": True}],
}
OUT.mkdir(exist_ok=True)
(OUT / "LMS_API.postman_collection.json").write_text(json.dumps(collection, indent=2))
(OUT / "LMS_Local.postman_environment.json").write_text(json.dumps(environment, indent=2))
print("wrote postman collection + environment")
