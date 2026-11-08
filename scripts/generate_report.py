"""Turn a JUnit XML file into a human-readable test execution report (HTML + Markdown).

Usage:
    python scripts/generate_report.py                       # reads reports/junit.xml
    python scripts/generate_report.py path/to/junit.xml     # custom input
Outputs: reports/test_execution_report.html and reports/test_execution_report.md

The report is built ONLY from the results found in the XML file. Nothing is invented:
if the file does not exist (tests have not been run) the script exits with a message.
"""
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / "reports" / "junit.xml"
OUT_DIR = ROOT / "reports"


def parse(path: Path):
    root = ET.parse(path).getroot()
    cases = []
    for tc in root.iter("testcase"):
        status, detail = "PASSED", ""
        for tag, label in (("failure", "FAILED"), ("error", "ERROR"), ("skipped", "SKIPPED")):
            node = tc.find(tag)
            if node is not None:
                status = label
                detail = (node.get("message") or "") + ("\n" + node.text if node.text else "")
                break
        cases.append({"suite": tc.get("classname", ""), "name": tc.get("name", ""),
                      "time": float(tc.get("time", 0) or 0), "status": status, "detail": detail.strip()})
    return cases


def summarize(cases):
    total = len(cases)
    counts = {s: sum(c["status"] == s for c in cases) for s in ("PASSED", "FAILED", "ERROR", "SKIPPED")}
    executed = counts["PASSED"] + counts["FAILED"] + counts["ERROR"]
    rate = (counts["PASSED"] / executed * 100) if executed else 0.0
    return total, counts, rate, sum(c["time"] for c in cases)


def to_markdown(cases, src, generated):
    total, n, rate, dur = summarize(cases)
    L = ["# Test Execution Report", "", f"- Source file: `{src}`", f"- Report generated: {generated}", "",
         "| Total | Passed | Failed | Errors | Skipped | Pass rate | Duration |", "|---|---|---|---|---|---|---|",
         f"| {total} | {n['PASSED']} | {n['FAILED']} | {n['ERROR']} | {n['SKIPPED']} | {rate:.1f}% | {dur:.1f}s |", "",
         "## Results", "", "| Status | Test | Module | Time (s) |", "|---|---|---|---|"]
    for c in sorted(cases, key=lambda c: (c["status"] == "PASSED", c["suite"], c["name"])):
        L.append(f"| {c['status']} | `{c['name']}` | {c['suite']} | {c['time']:.2f} |")
    bad = [c for c in cases if c["status"] in ("FAILED", "ERROR")]
    L += ["", "## Failure details", ""]
    L += ["No failures recorded in the source file."] if not bad else \
         [f"### {c['name']}\n\n```\n{c['detail']}\n```\n" for c in bad]
    return "\n".join(L) + "\n"


def to_html(cases, src, generated):
    total, n, rate, dur = summarize(cases)
    color = {"PASSED": "#1e7e34", "FAILED": "#c82333", "ERROR": "#c82333", "SKIPPED": "#856404"}
    rows = "".join(
        f"<tr><td style='color:{color[c['status']]};font-weight:bold'>{c['status']}</td>"
        f"<td>{escape(c['name'])}</td><td>{escape(c['suite'])}</td><td>{c['time']:.2f}</td></tr>"
        for c in sorted(cases, key=lambda c: (c["status"] == "PASSED", c["suite"], c["name"])))
    bad = [c for c in cases if c["status"] in ("FAILED", "ERROR")]
    details = "".join(f"<h3>{escape(c['name'])}</h3><pre>{escape(c['detail'])}</pre>" for c in bad) \
        or "<p>No failures recorded in the source file.</p>"
    card = lambda label, val, col: (f"<div class='card'><div class='v' style='color:{col}'>{val}</div>"
                                    f"<div>{label}</div></div>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Test Execution Report</title>
<style>body{{font-family:Arial,sans-serif;margin:2rem;color:#222}}table{{border-collapse:collapse;width:100%}}
td,th{{border:1px solid #ccc;padding:6px 10px;text-align:left;font-size:14px}}th{{background:#1f3864;color:#fff}}
.cards{{display:flex;gap:12px;margin:1rem 0}}.card{{border:1px solid #ccc;border-radius:6px;padding:10px 18px;text-align:center}}
.v{{font-size:28px;font-weight:bold}}pre{{background:#f6f6f6;padding:10px;overflow:auto}}</style></head><body>
<h1>Test Execution Report</h1><p>Source: <code>{escape(str(src))}</code><br>Report generated: {generated}</p>
<div class="cards">{card('Total', total, '#222')}{card('Passed', n['PASSED'], '#1e7e34')}
{card('Failed', n['FAILED'] + n['ERROR'], '#c82333')}{card('Skipped', n['SKIPPED'], '#856404')}
{card('Pass rate', f'{rate:.1f}%', '#222')}{card('Duration', f'{dur:.1f}s', '#222')}</div>
<h2>Results</h2><table><tr><th>Status</th><th>Test</th><th>Module</th><th>Time (s)</th></tr>{rows}</table>
<h2>Failure details</h2>{details}</body></html>"""


def main(argv):
    src = Path(argv[1]) if len(argv) > 1 else DEFAULT_IN
    if not src.exists():
        print(f"No results file found at {src}.\nRun the tests first (e.g. `pytest`), then re-run this script.")
        return 1
    cases = parse(src)
    if not cases:
        print(f"{src} contains no test cases; nothing to report.")
        return 1
    out_dir = Path(argv[2]) if len(argv) > 2 else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    (out_dir / "test_execution_report.md").write_text(to_markdown(cases, src.name, generated), encoding="utf-8")
    (out_dir / "test_execution_report.html").write_text(to_html(cases, src.name, generated), encoding="utf-8")
    total, n, rate, _ = summarize(cases)
    print(f"Report written to {out_dir}: {total} tests, {n['PASSED']} passed, "
          f"{n['FAILED'] + n['ERROR']} failed, {n['SKIPPED']} skipped ({rate:.1f}% pass rate)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
