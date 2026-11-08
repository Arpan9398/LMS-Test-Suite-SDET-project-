# Sample Bug Report

> **SAMPLE / TEMPLATE ONLY.** The scenario below is **illustrative**. It is **not** a defect found in the
> bundled demo LMS or in any real system. Do not treat it as a verified finding.
> Copy this file (e.g. `docs/BUG-001.md`), replace the example content with an issue you have actually
> reproduced, and fill in every field.

---

## BUG-SAMPLE-001 — Enrollment confirmation message shows wrong course name (illustrative example)

| Field | Value |
|---|---|
| **Bug ID** | BUG-SAMPLE-001 |
| **Status** | Example only (not a real defect) |
| **Module** | Course Enrollment |
| **Severity** | Medium *(Blocker / Critical / Major / Medium / Minor / Trivial)* |
| **Priority** | P2 *(P1 fix now · P2 next release · P3 backlog)* |
| **Reported by** | `<your name>` |
| **Date reported** | `<YYYY-MM-DD>` |
| **Found in version / build** | `<version or commit>` |
| **Environment** | OS: `<e.g. Windows 11>` · Browser: `<e.g. Chromium 1xx>` · URL: `<base URL>` |
| **Related test case** | TC-ENR-002 |
| **Reproducibility** | `<Always / Sometimes (x of y attempts) / Once>` |

### Summary
One sentence describing the problem. *Example: After enrolling in a course, the confirmation message names a different course than the one selected.*

### Preconditions
- Logged in as `student1` (not enrolled in any course).
- Course catalog contains C101 *Introduction to Python* and C102 *Software Testing Fundamentals*.

### Steps to Reproduce
1. Open `/login` and sign in as `student1`.
2. Navigate to **Courses**.
3. Click **Enroll** on **Introduction to Python (C101)**.
4. Read the confirmation message at the top of the page.

### Expected Result
Message reads: *"Successfully enrolled in Introduction to Python."* — the course the student selected.

### Actual Result
*(Example text — what you actually observed, stated factually.)*
Message names a different course, e.g. *"Successfully enrolled in Software Testing Fundamentals."*

### Evidence
- Screenshot: `screenshots/<file>.png` (Playwright saves failure screenshots automatically)
- Test that failed (if automated): `tests/ui/test_enrollment.py::test_student_can_enroll_in_course`
- Logs / HAR / API response: `<attach or paste>`

### Impact
Who is affected and how badly. *Example: Students may believe they joined the wrong course.*

### Workaround
`<None / describe>`

### Additional Notes
Anything that helps triage: regression? first seen in which build? related tickets?

---

## Quality checklist before filing a real bug
- [ ] Reproduced at least twice (or noted that it is intermittent)
- [ ] Steps start from a known state and contain no unnecessary actions
- [ ] Expected result is based on a requirement, spec or test case ID
- [ ] Actual result describes only what was observed — no guesses about root cause
- [ ] Evidence attached (screenshot, log, request/response)
- [ ] Checked for duplicates in the issue tracker
