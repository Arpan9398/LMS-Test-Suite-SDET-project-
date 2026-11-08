"""Minimal mock LMS used as the system under test (SUT).

It exposes a small web UI and a JSON API so the whole suite (Playwright UI tests,
pytest API tests, Postman/Newman) can run with zero external dependencies.
State is held in memory and can be reset via POST /api/test/reset.

Run standalone:  python -m app.lms_app        (listens on http://127.0.0.1:5000)
NOTE: This is a teaching/demo app, not production code.
"""
import copy
import secrets
from datetime import date

from flask import (Flask, flash, get_flashed_messages, jsonify, redirect,
                   render_template_string, request, session, url_for)

MAX_UPLOAD_BYTES = 1024 * 1024  # 1 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

SEED = {
    "users": {
        "student1": {"password": "Password123!", "name": "Alice Student", "locked": False},
        "student2": {"password": "Password456!", "name": "Bob Student", "locked": False},
        "locked_user": {"password": "Password123!", "name": "Locked User", "locked": True},
        "seeded_user": {"password": "Not-Used-1!", "name": "Seeded User", "locked": False},
    },
    "courses": {
        "C101": {"title": "Introduction to Python", "capacity": 30},
        "C102": {"title": "Software Testing Fundamentals", "capacity": 30},
        "C103": {"title": "Web Automation with Playwright", "capacity": 1},
    },
    "assignments": {
        "A101": {"course": "C101", "title": "Python Basics Exercise", "due": "2099-12-31"},
        "A102": {"course": "C102", "title": "Write a Test Plan", "due": "2099-12-31"},
        "A103": {"course": "C101", "title": "Legacy Assignment (closed)", "due": "2020-01-01"},
    },
    # seeded_user already holds the only seat of C103, so C103 is "Full"
    "enrollments": {"seeded_user": ["C103"]},
    "submissions": {},
}

STATE = {}
TOKENS = {}


def reset_state():
    STATE.clear()
    STATE.update(copy.deepcopy(SEED))
    STATE["enrollments"] = {u: set(c) for u, c in SEED["enrollments"].items()}
    TOKENS.clear()


def seats_taken(course_id):
    return sum(course_id in c for c in STATE["enrollments"].values())


def course_view(course_id, username):
    c = STATE["courses"][course_id]
    taken = seats_taken(course_id)
    return {
        "id": course_id, "title": c["title"], "capacity": c["capacity"],
        "seats_left": c["capacity"] - taken,
        "full": taken >= c["capacity"],
        "enrolled": course_id in STATE["enrollments"].get(username, set()),
    }


def check_submission(username, assignment_id, text, filename, size):
    """Shared business rules. Returns (status_code, message_or_None)."""
    a = STATE["assignments"].get(assignment_id)
    if not a:
        return 404, "Assignment not found"
    if a["course"] not in STATE["enrollments"].get(username, set()):
        return 403, "You must be enrolled in this course"
    if date.fromisoformat(a["due"]) < date.today():
        return 422, "Assignment is past due"
    if not (text or "").strip() and not filename:
        return 400, "Submission cannot be empty"
    if filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            return 400, "File type not allowed (use .pdf, .txt or .docx)"
        if size > MAX_UPLOAD_BYTES:
            return 400, "File is too large (max 1 MB)"
    return 201, None


def save_submission(username, assignment_id, text, filename):
    key = f"{username}:{assignment_id}"
    prev = STATE["submissions"].get(key)
    attempt = (prev["attempt"] + 1) if prev else 1
    STATE["submissions"][key] = {"attempt": attempt, "text": text, "filename": filename}
    return STATE["submissions"][key]


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{{ title }} - Demo LMS</title>
<style>body{font-family:Arial,sans-serif;margin:2rem;max-width:760px}nav a{margin-right:1rem}
.card{border:1px solid #ccc;padding:.75rem;margin:.5rem 0;border-radius:6px}
.msg{padding:.5rem;margin:.5rem 0;border-radius:4px}.error{background:#fde8e8}.success{background:#e6f6e6}</style></head><body>
{% if user %}<nav data-testid="nav"><a href="/dashboard">Dashboard</a><a href="/courses">Courses</a>
<a href="/my-courses">My Courses</a><a href="/assignments">Assignments</a>
<a href="/logout" data-testid="logout-link">Logout</a></nav>{% endif %}
{% for cat, m in messages %}<div class="msg {{ cat }}" data-testid="{{ tid or 'flash' }}-message" role="alert">{{ m }}</div>{% endfor %}
{{ body|safe }}</body></html>"""


def create_app():
    app = Flask(__name__)
    app.secret_key = "demo-only-secret"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    reset_state()

    def render(title, body, tid=None, **ctx):
        from markupsafe import Markup
        msgs = get_flashed_messages(with_categories=True)
        return render_template_string(PAGE, title=title, body=Markup(render_template_string(body, **ctx)),
                                      user=session.get("user"), messages=msgs, tid=tid)

    def login_required(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*a, **kw):
            if not session.get("user"):
                return redirect(url_for("login"))
            return fn(*a, **kw)
        return wrapper

    # ------------------------------ UI ------------------------------
    @app.get("/")
    def index():
        return redirect(url_for("dashboard" if session.get("user") else "login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            u = request.form.get("username", "").strip()
            p = request.form.get("password", "")
            user = STATE["users"].get(u)
            if not u or not p:
                flash("Username and password are required.", "error")
            elif not user or user["password"] != p:
                flash("Invalid username or password.", "error")
            elif user["locked"]:
                flash("Your account is locked. Contact support.", "error")
            else:
                session["user"] = u
                return redirect(url_for("dashboard"))
        return render("Login", """<h1>Login</h1>
<form method="post" novalidate>
<p><label>Username <input id="username" name="username" data-testid="username"></label></p>
<p><label>Password <input id="password" name="password" type="password" data-testid="password"></label></p>
<button type="submit" data-testid="login-button">Log in</button></form>""", tid="login-error")

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        name = STATE["users"][session["user"]]["name"]
        return render("Dashboard", '<h1 data-testid="welcome">Welcome, {{ name }}</h1>', name=name)

    @app.get("/courses")
    @login_required
    def courses():
        u = session["user"]
        views = [course_view(cid, u) for cid in STATE["courses"]]
        return render("Courses", """<h1>Course Catalog</h1>
{% for c in views %}<div class="card" data-testid="course-card-{{ c.id }}">
<h3 data-testid="course-title-{{ c.id }}">{{ c.title }}</h3><p>Seats left: {{ c.seats_left }}</p>
{% if c.enrolled %}<span data-testid="enrolled-badge-{{ c.id }}">Enrolled</span>
{% elif c.full %}<button disabled data-testid="full-badge-{{ c.id }}">Full</button>
{% else %}<form method="post" action="/courses/{{ c.id }}/enroll">
<button data-testid="enroll-{{ c.id }}">Enroll</button></form>{% endif %}</div>{% endfor %}""",
                      tid="enroll", views=views)

    @app.post("/courses/<cid>/enroll")
    @login_required
    def enroll_ui(cid):
        u = session["user"]
        if cid not in STATE["courses"]:
            flash("Course not found.", "error")
        elif course_view(cid, u)["enrolled"]:
            flash("You are already enrolled in this course.", "error")
        elif course_view(cid, u)["full"]:
            flash("This course is full.", "error")
        else:
            STATE["enrollments"].setdefault(u, set()).add(cid)
            flash(f"Successfully enrolled in {STATE['courses'][cid]['title']}.", "success")
        return redirect(url_for("courses"))

    @app.get("/my-courses")
    @login_required
    def my_courses():
        u = session["user"]
        mine = [course_view(c, u) for c in sorted(STATE["enrollments"].get(u, set()))]
        return render("My Courses", """<h1>My Courses</h1>
{% if not mine %}<p data-testid="no-courses">You are not enrolled in any courses.</p>{% endif %}
<ul data-testid="my-courses-list">{% for c in mine %}<li data-testid="my-course-{{ c.id }}">{{ c.title }}</li>{% endfor %}</ul>""",
                      mine=mine)

    @app.get("/assignments")
    @login_required
    def assignments():
        u = session["user"]
        enrolled = STATE["enrollments"].get(u, set())
        items = [dict(id=i, **a) for i, a in STATE["assignments"].items() if a["course"] in enrolled]
        return render("Assignments", """<h1>Assignments</h1>
{% if not items %}<p data-testid="no-assignments">No assignments available.</p>{% endif %}
{% for a in items %}<div class="card" data-testid="assignment-{{ a.id }}">
<a href="/assignments/{{ a.id }}" data-testid="open-{{ a.id }}">{{ a.title }}</a> (due {{ a.due }})</div>{% endfor %}""",
                      items=items)

    @app.route("/assignments/<aid>", methods=["GET", "POST"])
    @login_required
    def assignment_detail(aid):
        u = session["user"]
        a = STATE["assignments"].get(aid)
        if not a:
            return render("Not found", "<h1>Assignment not found</h1>"), 404
        if a["course"] not in STATE["enrollments"].get(u, set()):
            return render("Forbidden", '<h1 data-testid="forbidden">You must be enrolled in this course</h1>'), 403
        if request.method == "POST":
            text = request.form.get("text", "")
            f = request.files.get("file")
            fname = f.filename if f and f.filename else None
            data = f.read() if fname else b""
            status, msg = check_submission(u, aid, text, fname, len(data))
            if status == 201:
                s = save_submission(u, aid, text, fname)
                flash(f"Assignment submitted successfully (attempt {s['attempt']}).", "success")
            else:
                flash(msg, "error")
            return redirect(url_for("assignment_detail", aid=aid))
        sub = STATE["submissions"].get(f"{u}:{aid}")
        return render(a["title"], """<h1 data-testid="assignment-title">{{ a.title }}</h1><p>Due: {{ a.due }}</p>
<p>Status: <span data-testid="submission-status">{{ 'Submitted (attempt %d)' % sub.attempt if sub else 'Not submitted' }}</span></p>
<form method="post" enctype="multipart/form-data">
<p><textarea id="submission-text" name="text" rows="5" cols="50" data-testid="submission-text"></textarea></p>
<p><input type="file" name="file" data-testid="submission-file"></p>
<button type="submit" data-testid="submit-assignment">Submit</button></form>""",
                      tid="submission", a=a, sub=sub)

    # ------------------------------ API ------------------------------
    def api_user():
        auth = request.headers.get("Authorization", "")
        return TOKENS.get(auth.removeprefix("Bearer ").strip()) if auth.startswith("Bearer ") else None

    def unauthorized():
        return jsonify(error="Authentication required"), 401

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.post("/api/test/reset")
    def api_reset():
        reset_state()
        return jsonify(status="reset")

    @app.post("/api/auth/login")
    def api_login():
        body = request.get_json(silent=True) or {}
        u, p = body.get("username"), body.get("password")
        if not u or not p:
            return jsonify(error="username and password are required"), 400
        user = STATE["users"].get(u)
        if not user or user["password"] != p:
            return jsonify(error="Invalid credentials"), 401
        if user["locked"]:
            return jsonify(error="Account locked"), 423
        token = secrets.token_hex(16)
        TOKENS[token] = u
        return jsonify(token=token, user={"username": u, "name": user["name"]})

    @app.get("/api/courses")
    def api_courses():
        u = api_user()
        if not u:
            return unauthorized()
        return jsonify(courses=[course_view(c, u) for c in STATE["courses"]])

    @app.post("/api/courses/<cid>/enroll")
    def api_enroll(cid):
        u = api_user()
        if not u:
            return unauthorized()
        if cid not in STATE["courses"]:
            return jsonify(error="Course not found"), 404
        v = course_view(cid, u)
        if v["enrolled"]:
            return jsonify(error="Already enrolled"), 409
        if v["full"]:
            return jsonify(error="Course is full"), 409
        STATE["enrollments"].setdefault(u, set()).add(cid)
        return jsonify(enrollment={"course_id": cid, "username": u}), 201

    @app.get("/api/enrollments")
    def api_enrollments():
        u = api_user()
        if not u:
            return unauthorized()
        return jsonify(enrollments=sorted(STATE["enrollments"].get(u, set())))

    @app.post("/api/assignments/<aid>/submissions")
    def api_submit(aid):
        u = api_user()
        if not u:
            return unauthorized()
        body = request.get_json(silent=True) or {}
        status, msg = check_submission(u, aid, body.get("text"), None, 0)
        if status != 201:
            return jsonify(error=msg), status
        s = save_submission(u, aid, body.get("text"), None)
        return jsonify(submission={"assignment_id": aid, "attempt": s["attempt"]}), 201

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
