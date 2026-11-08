"""UI tests: Assignment submission (manual cases TC-ASG-xxx)."""
import pytest
from playwright.sync_api import expect


@pytest.fixture
def enrolled_in_python(logged_in, courses_page, test_data):
    courses_page.open().enroll(test_data["courses"]["python"]["id"])


@pytest.mark.ui
@pytest.mark.regression
def test_assignments_list_shows_only_enrolled_course_assignments(
        enrolled_in_python, assignments_page, test_data):
    """TC-ASG-001"""
    a = test_data["assignments"]
    assignments_page.open()
    expect(assignments_page.item(a["python_basics"]["id"])).to_be_visible()
    expect(assignments_page.item(a["test_plan"]["id"])).to_have_count(0)  # not enrolled in C102


@pytest.mark.ui
@pytest.mark.smoke
def test_submit_text_assignment_successfully(enrolled_in_python, assignments_page, test_data):
    """TC-ASG-002"""
    a = test_data["assignments"]["python_basics"]
    detail = assignments_page.open().open_assignment(a["id"])
    expect(detail.status).to_have_text("Not submitted")
    detail.submit_text(test_data["submission_text"])
    expect(detail.message).to_contain_text("submitted successfully")
    expect(detail.status).to_have_text("Submitted (attempt 1)")


@pytest.mark.ui
@pytest.mark.smoke
def test_submit_file_assignment_successfully(enrolled_in_python, assignment_detail_page, test_data, tmp_path):
    """TC-ASG-003"""
    f = tmp_path / "answer.txt"
    f.write_text("my answer")
    a = test_data["assignments"]["python_basics"]
    detail = assignment_detail_page.open_by_id(a["id"])
    detail.attach_file(path=f).submit()
    expect(detail.message).to_contain_text("submitted successfully")


@pytest.mark.ui
@pytest.mark.regression
def test_submit_without_content_shows_error(enrolled_in_python, assignment_detail_page, test_data):
    """TC-ASG-004"""
    a = test_data["assignments"]["python_basics"]
    detail = assignment_detail_page.open_by_id(a["id"]).submit()
    expect(detail.message).to_have_text(test_data["errors"]["empty_submission"])
    expect(detail.status).to_have_text("Not submitted")


@pytest.mark.ui
@pytest.mark.regression
def test_submit_disallowed_file_type_is_rejected(enrolled_in_python, assignment_detail_page, test_data):
    """TC-ASG-005"""
    a = test_data["assignments"]["python_basics"]
    detail = assignment_detail_page.open_by_id(a["id"])
    detail.attach_file(name="malware.exe", content=b"MZ").submit()
    expect(detail.message).to_contain_text(test_data["errors"]["bad_file_type"])


@pytest.mark.ui
@pytest.mark.regression
def test_submit_oversized_file_is_rejected(enrolled_in_python, assignment_detail_page, test_data):
    """TC-ASG-006"""
    a = test_data["assignments"]["python_basics"]
    too_big = b"x" * (test_data["max_upload_bytes"] + 1)
    detail = assignment_detail_page.open_by_id(a["id"])
    detail.attach_file(name="big.pdf", mime="application/pdf", content=too_big).submit()
    expect(detail.message).to_contain_text(test_data["errors"]["file_too_large"])


@pytest.mark.ui
@pytest.mark.regression
def test_past_due_assignment_rejects_submission(enrolled_in_python, assignment_detail_page, test_data):
    """TC-ASG-007"""
    a = test_data["assignments"]["past_due"]
    detail = assignment_detail_page.open_by_id(a["id"])
    detail.submit_text(test_data["submission_text"])
    expect(detail.message).to_have_text(test_data["errors"]["past_due"])


@pytest.mark.ui
@pytest.mark.regression
def test_unenrolled_student_cannot_open_assignment(logged_in, page, base_url, test_data):
    """TC-ASG-008"""
    a = test_data["assignments"]["python_basics"]
    response = page.goto(f"{base_url}/assignments/{a['id']}")
    assert response.status == 403
    expect(page.get_by_test_id("forbidden")).to_be_visible()


@pytest.mark.ui
@pytest.mark.regression
def test_resubmission_increments_attempt(enrolled_in_python, assignment_detail_page, test_data):
    """TC-ASG-009"""
    a = test_data["assignments"]["python_basics"]
    detail = assignment_detail_page.open_by_id(a["id"])
    detail.submit_text("first answer")
    expect(detail.status).to_have_text("Submitted (attempt 1)")
    detail.submit_text("second answer")
    expect(detail.status).to_have_text("Submitted (attempt 2)")
