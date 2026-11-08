"""Thin requests wrapper for the LMS REST API (reused by API tests)."""
import requests


class LmsApiClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token = None

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self, auth: bool = True) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if auth and self.token else {}

    def health(self):
        return self.session.get(self._url("/api/health"), timeout=self.timeout)

    def reset(self):
        return self.session.post(self._url("/api/test/reset"), timeout=self.timeout)

    def login(self, username, password, remember_token: bool = True):
        r = self.session.post(self._url("/api/auth/login"),
                              json={"username": username, "password": password}, timeout=self.timeout)
        if remember_token and r.status_code == 200:
            self.token = r.json()["token"]
        return r

    def list_courses(self, auth: bool = True):
        return self.session.get(self._url("/api/courses"), headers=self._headers(auth), timeout=self.timeout)

    def enroll(self, course_id):
        return self.session.post(self._url(f"/api/courses/{course_id}/enroll"),
                                 headers=self._headers(), timeout=self.timeout)

    def enrollments(self):
        return self.session.get(self._url("/api/enrollments"), headers=self._headers(), timeout=self.timeout)

    def submit_assignment(self, assignment_id, text):
        return self.session.post(self._url(f"/api/assignments/{assignment_id}/submissions"),
                                 json={"text": text}, headers=self._headers(), timeout=self.timeout)
