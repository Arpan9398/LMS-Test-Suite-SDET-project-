# LMS Test Suite (SDET Project)

End-to-end test automation sample for a Learning Management System (LMS), covering **login**,
**course enrollment** and **assignment submission**.

**Tech stack:** Python · pytest · Playwright · Postman · Newman · Excel (openpyxl)

The project ships with a small **mock LMS** (Flask) so everything runs locally with no external
system. You can point the same tests at a real LMS (see [Using a real LMS](#using-a-real-lms)).

---

## 1. Project structure

```
lms-test-suite/
├── app/                      Mock LMS (system under test): web UI + REST API
│   └── lms_app.py
├── config/settings.py        Base URL, browser, headless, timeouts (env-var driven)
├── data/test_data.json       Users, courses, assignments, expected messages
├── pages/                    Page Object Model (reusable Playwright code)
│   ├── base_page.py  login_page.py  courses_page.py  assignment_page.py
├── utils/
│   ├── api_client.py         Reusable requests wrapper for the LMS API
│   └── helpers.py            Test-data loader
├── tests/
│   ├── ui/                   Playwright + pytest: test_login / test_enrollment / test_assignment
│   └── api/test_api.py       pytest + requests API tests
├── postman/                  Postman collection + environment (run with Newman)
├── testcases/LMS_Manual_Test_Cases.xlsx   33 manual test cases + summary sheet
├── docs/BUG_REPORT_SAMPLE.md Bug report template with an illustrative example
├── scripts/                  run_tests.sh/.bat, run_newman.sh, generate_report.py, builders
├── reports/                  Generated: junit.xml, test_execution_report.html/.md
├── screenshots/              Generated: screenshots of failed UI tests
├── conftest.py               Fixtures (live app, browser, page objects, API client)
├── pytest.ini                Markers + JUnit output
└── requirements.txt
```

## 2. Setup

Prerequisites: **Python 3.10+**, and (only for Newman) **Node.js 18+**.

```bash
# from the project root
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium          # downloads the browser Playwright drives

# optional – only for the Postman collection
npm install -g newman
```

## 3. Running the tests

| Goal | Command |
|---|---|
| Everything + execution report | `./scripts/run_tests.sh` (Windows: `scripts\run_tests.bat`) |
| All tests (no report step) | `pytest` |
| UI tests only | `pytest -m ui` |
| API tests only | `pytest -m api` |
| Smoke tests only | `pytest -m smoke` |
| One file | `pytest tests/ui/test_login.py` |
| One test | `pytest -k test_student_can_enroll_in_course` |
| Watch the browser | `HEADLESS=false SLOW_MO=300 pytest -m ui` (Windows PowerShell: `$env:HEADLESS="false"; pytest -m ui`) |
| Another browser | `BROWSER=firefox pytest -m ui` (after `playwright install firefox`) |

`pytest` starts the bundled mock LMS automatically on a free port and resets its data before every
test, so tests are independent and can run in any order.

### Postman / Newman

```bash
./scripts/run_newman.sh              # starts the mock LMS, runs the collection, writes reports/newman-*.xml/html
```

Or manually: start the app (`python -m app.lms_app`) and run

```bash
newman run postman/LMS_API.postman_collection.json -e postman/LMS_Local.postman_environment.json
```

You can also import both JSON files into the Postman desktop app. Requests must be run **in order**
(the login request stores the token used by later requests).

### Excel manual test cases

Open `testcases/LMS_Manual_Test_Cases.xlsx`, execute the cases by hand, and fill in the yellow columns
(*Actual Result, Status, Executed By, Execution Date, Remarks*). The **Summary** sheet recalculates
automatically. All cases start as **Not Run** — nothing has been executed manually in the shipped file.
To regenerate the workbook: `python scripts/build_testcases_xlsx.py`.

## 4. Test execution report

`pytest` writes `reports/junit.xml` (configured in `pytest.ini`). Convert it into a readable report:

```bash
python scripts/generate_report.py
# -> reports/test_execution_report.html  and  reports/test_execution_report.md
```

The report lists totals, pass rate, every test with its status, and the failure details.
It is built **only** from the XML produced by a real run; if no run exists the script says so
instead of producing numbers. Failed UI tests also save a full-page screenshot in `screenshots/`.

## 5. Test data (mock LMS)

| Item | Value |
|---|---|
| Student | `student1` / `Password123!` |
| Second student | `student2` / `Password456!` |
| Locked account | `locked_user` / `Password123!` |
| Courses | C101 Introduction to Python · C102 Software Testing Fundamentals · C103 Web Automation with Playwright (**full**, capacity 1) |
| Assignments | A101 (C101, open) · A102 (C102, open) · A103 (C101, **past due**) |
| Upload rules | `.pdf`, `.txt`, `.docx` only, max 1 MB |

Edit `data/test_data.json` to change data used by the tests.

## 6. Coverage map

| Area | Manual (Excel) | UI automation | API (pytest) | Postman |
|---|---|---|---|---|
| Login | TC-LOGIN-001…012 | `test_login.py` | login tests | folder 02 |
| Enrollment | TC-ENR-001…010 | `test_enrollment.py` | enroll tests | folders 03–04 |
| Assignment submission | TC-ASG-001…011 | `test_assignment.py` | submission tests | folder 05 |

Each automated UI test names its manual test-case ID in its docstring, and the Excel sheet's
*Automation Reference* column points back to the test. Cases with *Automated? = No* are manual-only
(visual, accessibility, browser-history checks).

## 7. Using a real LMS

1. Set the base URL: `LMS_BASE_URL=https://your-lms.example.com pytest`
2. Update `data/test_data.json` (users, course IDs, messages) and the locators in `pages/`
   (they use `data-testid` attributes; adjust to your app's selectors).
3. The per-test data reset only exists in the mock app, so for a real LMS use dedicated test accounts and
   clean up (or use fresh data) between runs. Some tests rely on mock-specific seed data
   (full course C103, past-due assignment A103, locked user) and will need equivalents.
4. Postman: duplicate `LMS_Local.postman_environment.json`, change `baseUrl`/credentials, and skip folder `00 Setup`.

## 8. Troubleshooting

- *Browser not found* → run `playwright install chromium`.
- *`ModuleNotFoundError: app/pages/utils`* → run `pytest` from the project root (where `pytest.ini` is).
- *Port in use for Newman script* → stop whatever uses port 5000, or run the app on another port and edit the environment file.
- *Flaky UI timing* → raise `DEFAULT_TIMEOUT_MS`; tests use Playwright auto-waiting `expect(...)` assertions, avoid fixed sleeps.

## 9. Verification status of this package (read this)

This project was assembled in an offline sandbox where **pytest and Newman could not be installed**, so
the following was **not** done there: a real `pytest` run, a real Newman run, and therefore no official
execution report is included. What *was* verified in that sandbox:

- The mock LMS starts and behaves as documented.
- All 43 test cases (28 UI, 15 API) ran against the mock app using a temporary stand-in runner (not pytest)
  with real Playwright/Chromium: 43 passed, 0 failed. A deliberate temporary break of two app rules made
  4 of them fail as expected (then reverted).
- The Postman collection's 18 requests were replayed against the app and their expected status codes match.
  Its JavaScript assertions were **not** executed (that needs Newman).
- The Excel workbook recalculates with 0 formula errors; every automation reference points to an existing test.
- `scripts/generate_report.py` was exercised on pass, fail, skip and missing-file inputs.

Please run `./scripts/run_tests.sh` and `./scripts/run_newman.sh` on your machine for authoritative results.
No defects in any real system are claimed anywhere in this package; `docs/BUG_REPORT_SAMPLE.md` is a template.
