"""Regenerates testcases/LMS_Manual_Test_Cases.xlsx (run: python scripts/build_testcases_xlsx.py)."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parent.parent / "testcases" / "LMS_Manual_Test_Cases.xlsx"
HEAD = ["Test Case ID", "Module", "Title", "Priority", "Type", "Preconditions", "Test Steps", "Test Data",
        "Expected Result", "Actual Result", "Status", "Automated?", "Automation Reference",
        "Executed By", "Execution Date", "Remarks"]
UI = "tests/ui/"
S1 = "student1 / Password123!"

# (id, module, title, priority, type, preconditions, steps, data, expected, automation_ref)
CASES = [
 # ----------------------------- LOGIN -----------------------------
 ("TC-LOGIN-001", "Login", "Login with valid credentials", "High", "Positive", "Student account exists and is active.",
  "1. Open /login\n2. Enter valid username\n3. Enter valid password\n4. Click 'Log in'", S1,
  "User lands on /dashboard and sees 'Welcome, Alice Student'.", UI + "test_login.py::test_login_with_valid_credentials_redirects_to_dashboard"),
 ("TC-LOGIN-002", "Login", "Login with wrong password", "High", "Negative", "Student account exists.",
  "1. Open /login\n2. Enter valid username\n3. Enter wrong password\n4. Click 'Log in'", "student1 / WrongPass!",
  "Error 'Invalid username or password.' is shown; user stays on /login.", UI + "test_login.py::test_login_rejects_invalid_credentials[wrong_password]"),
 ("TC-LOGIN-003", "Login", "Login with unknown username", "Medium", "Negative", "None.",
  "1. Open /login\n2. Enter a username that does not exist\n3. Enter any password\n4. Click 'Log in'", "no_such_user / Password123!",
  "Error 'Invalid username or password.' is shown (does not reveal whether the user exists).", UI + "test_login.py::test_login_rejects_invalid_credentials[unknown_user]"),
 ("TC-LOGIN-004", "Login", "Login with empty username", "Medium", "Negative", "None.",
  "1. Open /login\n2. Leave username blank\n3. Enter password\n4. Click 'Log in'", "<blank> / Password123!",
  "Error 'Username and password are required.' is shown.", UI + "test_login.py::test_login_requires_both_fields[empty_username]"),
 ("TC-LOGIN-005", "Login", "Login with empty password", "Medium", "Negative", "None.",
  "1. Open /login\n2. Enter username\n3. Leave password blank\n4. Click 'Log in'", "student1 / <blank>",
  "Error 'Username and password are required.' is shown.", UI + "test_login.py::test_login_requires_both_fields[empty_password]"),
 ("TC-LOGIN-006", "Login", "Login with both fields empty", "Low", "Negative", "None.",
  "1. Open /login\n2. Leave both fields blank\n3. Click 'Log in'", "<blank> / <blank>",
  "Error 'Username and password are required.' is shown.", UI + "test_login.py::test_login_requires_both_fields[both_empty]"),
 ("TC-LOGIN-007", "Login", "Locked account cannot log in", "High", "Negative", "Account 'locked_user' is locked.",
  "1. Open /login\n2. Enter locked account credentials\n3. Click 'Log in'", "locked_user / Password123!",
  "Message states the account is locked; no session is created.", UI + "test_login.py::test_locked_account_cannot_login"),
 ("TC-LOGIN-008", "Login", "Logout ends the session", "High", "Positive", "User is logged in.",
  "1. Click 'Logout' in the navigation bar", S1,
  "User is returned to /login.", UI + "test_login.py::test_logout_returns_to_login_page"),
 ("TC-LOGIN-009", "Login", "Protected page redirects anonymous user to login", "High", "Security", "User is NOT logged in.",
  "1. Open /courses directly in the browser", "n/a",
  "User is redirected to /login.", UI + "test_login.py::test_protected_page_redirects_to_login_when_unauthenticated"),
 ("TC-LOGIN-010", "Login", "SQL-injection style input is rejected", "Medium", "Security", "None.",
  "1. Open /login\n2. Enter ' OR '1'='1 as username and password\n3. Click 'Log in'", "' OR '1'='1 / ' OR '1'='1",
  "Login fails with 'Invalid username or password.'; no session is created.", UI + "test_login.py::test_login_rejects_invalid_credentials[sql_injection_string]"),
 ("TC-LOGIN-011", "Login", "Password field masks characters", "Low", "UI", "None.",
  "1. Open /login\n2. Type text in the password field", "any text",
  "Typed characters are masked (shown as dots).", ""),
 ("TC-LOGIN-012", "Login", "Browser Back after logout does not expose data", "Medium", "Security", "User is logged in and has opened /courses.",
  "1. Click 'Logout'\n2. Click the browser Back button", S1,
  "Protected content is not usable; a request for protected data redirects to /login.", ""),
 # --------------------------- ENROLLMENT ---------------------------
 ("TC-ENR-001", "Course Enrollment", "Course catalog lists available courses", "High", "Positive", "Logged in as a student.",
  "1. Click 'Courses'", S1,
  "Catalog shows C101, C102 and C103 with their titles.", UI + "test_enrollment.py::test_course_catalog_lists_available_courses"),
 ("TC-ENR-002", "Course Enrollment", "Student enrolls in an open course", "High", "Positive", "Logged in; not enrolled in C101.",
  "1. Open 'Courses'\n2. Click 'Enroll' on 'Introduction to Python'", "Course C101",
  "Message 'Successfully enrolled in Introduction to Python.' is shown.", UI + "test_enrollment.py::test_student_can_enroll_in_course"),
 ("TC-ENR-003", "Course Enrollment", "Enrolled course appears in My Courses", "High", "Positive", "Logged in; enrolled in C101.",
  "1. Open 'My Courses'", "Course C101",
  "'Introduction to Python' is listed.", UI + "test_enrollment.py::test_enrolled_course_appears_in_my_courses"),
 ("TC-ENR-004", "Course Enrollment", "Enroll button replaced by 'Enrolled' badge", "Medium", "Positive", "Logged in; just enrolled in C101.",
  "1. Stay on 'Courses' after enrolling", "Course C101",
  "'Enrolled' badge is visible; 'Enroll' button is gone (prevents duplicate enrollment).", UI + "test_enrollment.py::test_enrolled_course_shows_badge_instead_of_enroll_button"),
 ("TC-ENR-005", "Course Enrollment", "Full course cannot be enrolled", "High", "Negative", "Logged in; C103 has no seats left.",
  "1. Open 'Courses'\n2. Look at 'Web Automation with Playwright'", "Course C103 (capacity 1, 1 taken)",
  "Only a disabled 'Full' button is shown; no 'Enroll' button.", UI + "test_enrollment.py::test_full_course_cannot_be_enrolled"),
 ("TC-ENR-006", "Course Enrollment", "Enrollment pages require login", "High", "Security", "User is NOT logged in.",
  "1. Open /my-courses directly", "n/a",
  "User is redirected to /login.", UI + "test_enrollment.py::test_enrollment_requires_login"),
 ("TC-ENR-007", "Course Enrollment", "Enroll in multiple courses", "Medium", "Positive", "Logged in; not enrolled in anything.",
  "1. Enroll in C101\n2. Enroll in C102\n3. Open 'My Courses'", "C101, C102",
  "Both courses are listed.", UI + "test_enrollment.py::test_student_can_enroll_in_multiple_courses"),
 ("TC-ENR-008", "Course Enrollment", "Enrollment persists after logout/login", "Medium", "Positive", "Logged in.",
  "1. Enroll in C101\n2. Logout\n3. Login again\n4. Open 'My Courses'", S1,
  "C101 is still listed.", UI + "test_enrollment.py::test_enrollment_persists_after_relogin"),
 ("TC-ENR-009", "Course Enrollment", "Enrollment is private to each student", "Medium", "Security", "student1 enrolled in C101.",
  "1. Logout student1\n2. Login as student2\n3. Open 'My Courses'", "student2 / Password456!",
  "student2 sees 'You are not enrolled in any courses.'", UI + "test_enrollment.py::test_enrollment_is_per_student"),
 ("TC-ENR-010", "Course Enrollment", "Catalog layout is usable on a phone-sized screen", "Low", "UI", "Logged in.",
  "1. Open 'Courses' on a 375px-wide viewport", "n/a",
  "Cards are readable, buttons are tappable, no horizontal scrolling.", ""),
 # ----------------------------- ASSIGNMENT -----------------------------
 ("TC-ASG-001", "Assignment Submission", "Assignment list shows only enrolled courses", "Medium", "Positive", "Logged in; enrolled in C101 only.",
  "1. Open 'Assignments'", "A101 visible; A102 hidden",
  "'Python Basics Exercise' is listed; 'Write a Test Plan' (C102) is not.", UI + "test_assignment.py::test_assignments_list_shows_only_enrolled_course_assignments"),
 ("TC-ASG-002", "Assignment Submission", "Submit a text answer", "High", "Positive", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Type an answer\n3. Click 'Submit'", "Text: 'This is my answer for the assignment.'",
  "Message 'Assignment submitted successfully' is shown; status = 'Submitted (attempt 1)'.", UI + "test_assignment.py::test_submit_text_assignment_successfully"),
 ("TC-ASG-003", "Assignment Submission", "Submit a file (.txt)", "High", "Positive", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Choose a small .txt file\n3. Click 'Submit'", "answer.txt (< 1 MB)",
  "Submission succeeds with a success message.", UI + "test_assignment.py::test_submit_file_assignment_successfully"),
 ("TC-ASG-004", "Assignment Submission", "Empty submission is rejected", "High", "Negative", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Click 'Submit' without text or file", "n/a",
  "Error 'Submission cannot be empty'; status stays 'Not submitted'.", UI + "test_assignment.py::test_submit_without_content_shows_error"),
 ("TC-ASG-005", "Assignment Submission", "Disallowed file type is rejected", "High", "Negative", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Choose malware.exe\n3. Click 'Submit'", "malware.exe",
  "Error 'File type not allowed (use .pdf, .txt or .docx)'.", UI + "test_assignment.py::test_submit_disallowed_file_type_is_rejected"),
 ("TC-ASG-006", "Assignment Submission", "File larger than 1 MB is rejected", "Medium", "Boundary", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Choose a PDF of 1 MB + 1 byte\n3. Click 'Submit'", "big.pdf (1,048,577 bytes)",
  "Error 'File is too large (max 1 MB)'.", UI + "test_assignment.py::test_submit_oversized_file_is_rejected"),
 ("TC-ASG-007", "Assignment Submission", "Past-due assignment rejects submission", "High", "Negative", "Logged in; enrolled in C101.",
  "1. Open assignment A103 (due 2020-01-01)\n2. Type an answer\n3. Click 'Submit'", "A103",
  "Error 'Assignment is past due'; nothing is saved.", UI + "test_assignment.py::test_past_due_assignment_rejects_submission"),
 ("TC-ASG-008", "Assignment Submission", "Unenrolled student cannot open assignment", "High", "Security", "Logged in; NOT enrolled in C101.",
  "1. Open /assignments/A101 directly", "A101",
  "HTTP 403 page: 'You must be enrolled in this course'.", UI + "test_assignment.py::test_unenrolled_student_cannot_open_assignment"),
 ("TC-ASG-009", "Assignment Submission", "Resubmission increments attempt number", "Medium", "Positive", "Logged in; enrolled in C101.",
  "1. Submit an answer\n2. Submit a second answer", "'first answer', 'second answer'",
  "Status changes from 'Submitted (attempt 1)' to 'Submitted (attempt 2)'.", UI + "test_assignment.py::test_resubmission_increments_attempt"),
 ("TC-ASG-010", "Assignment Submission", "Submission form is keyboard accessible", "Low", "Accessibility", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Use only Tab/Shift+Tab/Enter to fill and submit", "n/a",
  "All controls are reachable in a logical order with a visible focus indicator.", ""),
 ("TC-ASG-011", "Assignment Submission", "Very long text answer is handled", "Low", "Boundary", "Logged in; enrolled in C101.",
  "1. Open assignment A101\n2. Paste ~50,000 characters\n3. Click 'Submit'", "50k characters",
  "Either accepted with success message, or a clear validation message is shown; no server error page.", ""),
]


def build():
    wb = Workbook()
    arial = Font(name="Arial", size=10)
    bold = Font(name="Arial", size=10, bold=True)
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    head_fill = PatternFill("solid", fgColor="1F3864")
    input_fill = PatternFill("solid", fgColor="FFF2CC")

    # ---- Read Me
    ws = wb.active
    ws.title = "Read Me"
    rows = [
        ("LMS Manual Test Cases", None),
        ("Purpose", "Manual test cases for Login, Course Enrollment and Assignment Submission."),
        ("System under test", "Bundled demo LMS (app/lms_app.py) or any LMS with equivalent behaviour. Start it with: python -m app.lms_app"),
        ("Test accounts", "student1 / Password123!   student2 / Password456!   locked_user (locked)"),
        ("How to use", "Fill ONLY the yellow columns on the 'Test Cases' sheet: Actual Result, Status, Executed By, Execution Date, Remarks."),
        ("Status values", "Not Run (default), Pass, Fail, Blocked, Skipped. The 'Summary' sheet recalculates automatically."),
        ("Execution state", "No manual execution has been recorded in this file. Every case is 'Not Run' until a tester updates it."),
        ("Automated?", "'Yes' means a pytest/Playwright test covers the case (see Automation Reference). 'No' means manual only."),
        ("Priority", "High = critical path / security; Medium = important; Low = nice-to-have."),
    ]
    for r, (a, b) in enumerate(rows, 1):
        ws.cell(r, 1, a).font = Font(name="Arial", size=14 if r == 1 else 10, bold=True)
        if b:
            ws.cell(r, 2, b).font = arial
            ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
    ws["A11"] = "Legend"; ws["A11"].font = bold
    ws["B11"] = "Yellow cell = tester input"; ws["B11"].fill = input_fill; ws["B11"].font = arial
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 110

    # ---- Test Cases
    tc = wb.create_sheet("Test Cases")
    tc.append(HEAD)
    for c in CASES:
        (cid, mod, title, pri, typ, pre, steps, data, exp, ref) = c
        tc.append([cid, mod, title, pri, typ, pre, steps, data, exp, None, "Not Run",
                   "Yes" if ref else "No", ref or "—", None, None, None])
    widths = [14, 22, 38, 10, 13, 32, 48, 30, 48, 30, 11, 11, 62, 14, 14, 28]
    for i, w in enumerate(widths, 1):
        tc.column_dimensions[tc.cell(1, i).column_letter].width = w
    last = tc.max_row
    for cell in tc[1]:
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        cell.fill = head_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    for row in tc.iter_rows(min_row=2, max_row=last):
        for cell in row:
            cell.font = arial
            cell.border = border
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        for idx in (9, 10, 13, 14, 15):  # J,K,N,O,P  (Actual, Status, Executed By, Date, Remarks)
            row[idx].fill = input_fill
        row[14].number_format = "yyyy-mm-dd"
    tc.freeze_panes = "D2"
    tc.auto_filter.ref = f"A1:P{last}"
    dv = DataValidation(type="list", formula1='"Not Run,Pass,Fail,Blocked,Skipped"', allow_blank=False)
    dv.add(f"K2:K{last}")
    tc.add_data_validation(dv)
    for text, color in (("Pass", "C6EFCE"), ("Fail", "FFC7CE"), ("Blocked", "FFEB9C")):
        tc.conditional_formatting.add(f"K2:K{last}", CellIsRule(operator="equal", formula=[f'"{text}"'],
                                      fill=PatternFill("solid", bgColor=color, fgColor=color)))

    # ---- Summary (all formulas)
    sm = wb.create_sheet("Summary")
    sm.append(["Module", "Total", "Pass", "Fail", "Blocked", "Skipped", "Not Run", "Automated", "Pass Rate (of executed)"])
    mods = ["Login", "Course Enrollment", "Assignment Submission"]
    rng = lambda col: f"'Test Cases'!${col}$2:${col}${last}"
    for i, m in enumerate(mods, 2):
        sm.append([m, f"=COUNTIF({rng('B')},A{i})"] +
                  [f'=COUNTIFS({rng("B")},$A{i},{rng("K")},"{s}")' for s in ("Pass", "Fail", "Blocked", "Skipped", "Not Run")] +
                  [f'=COUNTIFS({rng("B")},$A{i},{rng("L")},"Yes")',
                   f'=IFERROR(C{i}/(C{i}+D{i}),"n/a")'])
    t = len(mods) + 2
    sm.append(["TOTAL"] + [f"=SUM({c}2:{c}{t-1})" for c in "BCDEFGH"] + [f'=IFERROR(C{t}/(C{t}+D{t}),"n/a")'])
    for cell in sm[1]:
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF"); cell.fill = head_fill
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
    for row in sm.iter_rows(min_row=2, max_row=t):
        for cell in row:
            cell.font = bold if row[0].value == "TOTAL" else arial
            cell.border = border
        row[8].number_format = "0.0%"
    sm.column_dimensions["A"].width = 26
    for col in "BCDEFGHI":
        sm.column_dimensions[col].width = 14
    sm.column_dimensions["I"].width = 24
    sm.cell(t + 2, 1, "All values are formulas over the 'Test Cases' sheet; 'n/a' = nothing executed yet.").font = arial

    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(f"wrote {OUT} ({len(CASES)} cases)")


if __name__ == "__main__":
    build()
