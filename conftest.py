"""Shared fixtures: live mock LMS, Playwright browser/page, API client, test data."""
import logging
import threading

import pytest
from playwright.sync_api import sync_playwright

from config import settings
from pages.assignment_page import AssignmentDetailPage, AssignmentsPage
from pages.courses_page import CoursesPage, MyCoursesPage
from pages.login_page import LoginPage
from utils.api_client import LmsApiClient
from utils.helpers import load_test_data


# ---------------------------------------------------------------- data / env
@pytest.fixture(scope="session")
def test_data():
    return load_test_data()


@pytest.fixture(scope="session")
def base_url():
    """Use LMS_BASE_URL if provided, otherwise start the bundled mock LMS."""
    if settings.BASE_URL:
        yield settings.BASE_URL
        return
    from werkzeug.serving import make_server
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    from app.lms_app import create_app
    server = make_server("127.0.0.1", 0, create_app(), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(autouse=True)
def reset_lms_state(base_url):
    """Reset mock LMS data before every test for isolation (mock app only)."""
    if not settings.BASE_URL:
        LmsApiClient(base_url).reset()
    yield


# --------------------------------------------------------------- playwright
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as pw:
        launcher = getattr(pw, settings.BROWSER)
        b = launcher.launch(headless=settings.HEADLESS, slow_mo=settings.SLOW_MO)
        yield b
        b.close()


@pytest.fixture
def page(browser, request):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    context.set_default_timeout(settings.DEFAULT_TIMEOUT_MS)
    pg = context.new_page()
    yield pg
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        settings.SCREENSHOT_DIR.mkdir(exist_ok=True)
        safe = request.node.name.replace("/", "_").replace("[", "_").replace("]", "")
        pg.screenshot(path=str(settings.SCREENSHOT_DIR / f"{safe}.png"), full_page=True)
    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose pass/fail of each phase to fixtures (used for failure screenshots)."""
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


# ------------------------------------------------------------- page objects
@pytest.fixture
def login_page(page, base_url):
    return LoginPage(page, base_url)


@pytest.fixture
def courses_page(page, base_url):
    return CoursesPage(page, base_url)


@pytest.fixture
def my_courses_page(page, base_url):
    return MyCoursesPage(page, base_url)


@pytest.fixture
def assignments_page(page, base_url):
    return AssignmentsPage(page, base_url)


@pytest.fixture
def assignment_detail_page(page, base_url):
    return AssignmentDetailPage(page, base_url)


@pytest.fixture
def logged_in(login_page, test_data):
    """Log the default student in through the UI and return the login page."""
    u = test_data["users"]["student"]
    login_page.open().login(u["username"], u["password"])
    return login_page


# ---------------------------------------------------------------------- api
@pytest.fixture
def api(base_url):
    return LmsApiClient(base_url)


@pytest.fixture
def authed_api(api, test_data):
    u = test_data["users"]["student"]
    assert api.login(u["username"], u["password"]).status_code == 200
    return api
