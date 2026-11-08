"""UI tests: Course enrollment (manual cases TC-ENR-xxx)."""
import pytest
from playwright.sync_api import expect


@pytest.mark.ui
@pytest.mark.smoke
def test_course_catalog_lists_available_courses(logged_in, courses_page, test_data):
    """TC-ENR-001"""
    courses_page.open()
    for c in test_data["courses"].values():
        expect(courses_page.card(c["id"])).to_contain_text(c["title"])


@pytest.mark.ui
@pytest.mark.smoke
def test_student_can_enroll_in_course(logged_in, courses_page, test_data):
    """TC-ENR-002"""
    course = test_data["courses"]["python"]
    courses_page.open().enroll(course["id"])
    expect(courses_page.message).to_contain_text(f"Successfully enrolled in {course['title']}")


@pytest.mark.ui
@pytest.mark.regression
def test_enrolled_course_appears_in_my_courses(logged_in, courses_page, my_courses_page, test_data):
    """TC-ENR-003"""
    course = test_data["courses"]["python"]
    courses_page.open().enroll(course["id"])
    my_courses_page.open()
    expect(my_courses_page.course(course["id"])).to_have_text(course["title"])


@pytest.mark.ui
@pytest.mark.regression
def test_enrolled_course_shows_badge_instead_of_enroll_button(logged_in, courses_page, test_data):
    """TC-ENR-004"""
    cid = test_data["courses"]["python"]["id"]
    courses_page.open().enroll(cid)
    expect(courses_page.enrolled_badge(cid)).to_be_visible()
    expect(courses_page.enroll_button(cid)).to_have_count(0)


@pytest.mark.ui
@pytest.mark.regression
def test_full_course_cannot_be_enrolled(logged_in, courses_page, test_data):
    """TC-ENR-005"""
    cid = test_data["courses"]["full"]["id"]
    courses_page.open()
    expect(courses_page.full_button(cid)).to_be_disabled()
    expect(courses_page.enroll_button(cid)).to_have_count(0)


@pytest.mark.ui
@pytest.mark.regression
def test_enrollment_requires_login(page, base_url):
    """TC-ENR-006"""
    page.goto(f"{base_url}/my-courses")
    expect(page).to_have_url(f"{base_url}/login")


@pytest.mark.ui
@pytest.mark.regression
def test_student_can_enroll_in_multiple_courses(logged_in, courses_page, my_courses_page, test_data):
    """TC-ENR-007"""
    ids = [test_data["courses"]["python"]["id"], test_data["courses"]["testing"]["id"]]
    courses_page.open()
    for cid in ids:
        courses_page.enroll(cid)
    my_courses_page.open()
    for cid in ids:
        expect(my_courses_page.course(cid)).to_be_visible()


@pytest.mark.ui
@pytest.mark.regression
def test_enrollment_persists_after_relogin(logged_in, courses_page, my_courses_page, login_page, test_data):
    """TC-ENR-008"""
    u = test_data["users"]["student"]
    cid = test_data["courses"]["python"]["id"]
    courses_page.open().enroll(cid)
    login_page.logout()
    login_page.open().login(u["username"], u["password"])
    my_courses_page.open()
    expect(my_courses_page.course(cid)).to_be_visible()


@pytest.mark.ui
@pytest.mark.regression
def test_enrollment_is_per_student(logged_in, courses_page, my_courses_page, login_page, test_data):
    """TC-ENR-009"""
    cid = test_data["courses"]["python"]["id"]
    courses_page.open().enroll(cid)
    login_page.logout()
    other = test_data["users"]["student_two"]
    login_page.open().login(other["username"], other["password"])
    my_courses_page.open()
    expect(my_courses_page.empty_message).to_be_visible()
