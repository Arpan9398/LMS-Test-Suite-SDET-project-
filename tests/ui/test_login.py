"""UI tests: Login (manual cases TC-LOGIN-xxx)."""
import pytest
from playwright.sync_api import expect

from utils.helpers import load_test_data

DATA = load_test_data()


@pytest.mark.ui
@pytest.mark.smoke
def test_login_with_valid_credentials_redirects_to_dashboard(login_page, test_data):
    """TC-LOGIN-001"""
    u = test_data["users"]["student"]
    login_page.open().login(u["username"], u["password"])
    expect(login_page.page).to_have_url(f"{login_page.base_url}/dashboard")
    expect(login_page.welcome).to_have_text(f"Welcome, {u['display_name']}")


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.parametrize("case", DATA["invalid_logins"], ids=lambda c: c["id"])
def test_login_rejects_invalid_credentials(login_page, case):
    """TC-LOGIN-002 (wrong password), TC-LOGIN-003 (unknown user), TC-LOGIN-010 (SQL-like input)"""
    login_page.open().login(case["username"], case["password"])
    expect(login_page.error).to_have_text(case["error"])
    expect(login_page.page).to_have_url(f"{login_page.base_url}/login")


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.parametrize("case", DATA["empty_logins"], ids=lambda c: c["id"])
def test_login_requires_both_fields(login_page, case):
    """TC-LOGIN-004 (empty username), TC-LOGIN-005 (empty password), TC-LOGIN-006 (both empty)"""
    login_page.open().login(case["username"], case["password"])
    expect(login_page.error).to_have_text("Username and password are required.")


@pytest.mark.ui
@pytest.mark.regression
def test_locked_account_cannot_login(login_page, test_data):
    """TC-LOGIN-007"""
    u = test_data["users"]["locked"]
    login_page.open().login(u["username"], u["password"])
    expect(login_page.error).to_contain_text("locked")


@pytest.mark.ui
@pytest.mark.smoke
def test_logout_returns_to_login_page(logged_in):
    """TC-LOGIN-008"""
    logged_in.logout()
    expect(logged_in.page).to_have_url(f"{logged_in.base_url}/login")


@pytest.mark.ui
@pytest.mark.regression
def test_protected_page_redirects_to_login_when_unauthenticated(page, base_url):
    """TC-LOGIN-009"""
    page.goto(f"{base_url}/courses")
    expect(page).to_have_url(f"{base_url}/login")
