import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string

app = Flask(__name__)

ALERT_FILE = Path("alerts.log")
REPORT_FILE = Path("report.csv")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mini IDS Dashboard</title>
    <style>
        :root {
            --bg: #f5efe3;
            --ink: #1f2a30;
            --panel: rgba(255, 251, 244, 0.9);
            --accent: #b2472e;
            --line: rgba(31, 42, 48, 0.12);
            --muted: #5d6a70;
            --ok: #2d6a4f;
            --low: #4f6d7a;
            --medium: #9a6700;
            --high: #b54708;
            --critical: #b42318;
            --critical-soft: rgba(180, 35, 24, 0.12);
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Georgia, "Times New Roman", serif;
            color: var(--ink);
            background:
                radial-gradient(circle at top left, rgba(178, 71, 46, 0.16), transparent 28%),
                radial-gradient(circle at bottom right, rgba(45, 106, 79, 0.14), transparent 22%),
                linear-gradient(135deg, #f8f3ea, var(--bg));
            min-height: 100vh;
        }

        .shell {
            max-width: 1120px;
            margin: 0 auto;
            padding: 48px 20px 56px;
        }

        .hero {
            display: grid;
            gap: 16px;
            margin-bottom: 28px;
        }

        .eyebrow {
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font: 600 12px/1.2 Verdana, sans-serif;
            color: var(--accent);
        }

        .hero-top {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: end;
            flex-wrap: wrap;
        }

        h1 {
            margin: 0;
            font-size: clamp(2.4rem, 4vw, 4.6rem);
            line-height: 0.95;
        }

        .lead {
            max-width: 720px;
            margin: 0;
            color: var(--muted);
            font-size: 1.05rem;
        }

        .meta {
            color: var(--muted);
            font: 600 12px/1.4 Verdana, sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .status {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(45, 106, 79, 0.1);
            color: var(--ok);
            font: 600 13px/1.2 Verdana, sans-serif;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--ok);
            box-shadow: 0 0 0 6px rgba(45, 106, 79, 0.12);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }

        .grid-wide {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        .card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 18px 48px rgba(31, 42, 48, 0.08);
            backdrop-filter: blur(6px);
        }

        .card h2, .card h3, .card p {
            margin-top: 0;
        }

        .stat {
            font-size: 2.2rem;
            margin: 6px 0;
        }

        .muted {
            color: var(--muted);
            margin-bottom: 0;
        }

        .bar-stack {
            display: flex;
            height: 18px;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(31, 42, 48, 0.08);
            margin: 14px 0 18px;
        }

        .bar {
            height: 100%;
        }

        .bar.low { background: var(--low); }
        .bar.medium { background: var(--medium); }
        .bar.high { background: var(--high); }
        .bar.critical { background: var(--critical); }

        .legend {
            display: grid;
            gap: 10px;
        }

        .legend-row {
            display: grid;
            grid-template-columns: auto 1fr auto;
            align-items: center;
            gap: 10px;
        }

        .swatch {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .swatch.low { background: var(--low); }
        .swatch.medium { background: var(--medium); }
        .swatch.high { background: var(--high); }
        .swatch.critical { background: var(--critical); }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.96rem;
        }

        th, td {
            text-align: left;
            padding: 10px 8px;
            border-bottom: 1px solid var(--line);
            vertical-align: top;
        }

        th {
            font: 600 12px/1.2 Verdana, sans-serif;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 5px 10px;
            font: 700 11px/1 Verdana, sans-serif;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .badge.low {
            color: var(--low);
            background: rgba(79, 109, 122, 0.12);
        }

        .badge.medium {
            color: var(--medium);
            background: rgba(154, 103, 0, 0.12);
        }

        .badge.high {
            color: var(--high);
            background: rgba(181, 71, 8, 0.12);
        }

        .badge.critical {
            color: var(--critical);
            background: var(--critical-soft);
        }

        ul {
            list-style: none;
            padding-left: 0;
            margin-bottom: 0;
        }

        li + li {
            margin-top: 10px;
        }

        .alert-item {
            display: grid;
            gap: 8px;
            padding: 12px 0;
            border-bottom: 1px solid var(--line);
        }

        .alert-item:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .alert-top {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        .alert-text {
            margin: 0;
        }

        .alert-time {
            color: var(--muted);
            font: 600 11px/1.3 Verdana, sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .helper {
            font: 600 12px/1.4 Verdana, sans-serif;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        @media (max-width: 860px) {
            .grid-wide {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <main class="shell">
        <section class="hero">
            <div class="eyebrow">WSL Mini IDS</div>
            <div class="hero-top">
                <div>
                    <h1>Intrusion Detection Dashboard</h1>
                    <p class="lead">A lightweight dashboard for your Python log monitor showing recent detections, top source IPs, and current system health.</p>
                </div>
                <div class="meta">Last Updated<br>{{ last_updated }}</div>
            </div>
            <div class="status">
                <span class="status-dot"></span>
                <span>System status: Running</span>
            </div>
        </section>

        <section class="grid">
            <article class="card">
                <h2>Total Events</h2>
                <p class="stat">{{ total_events }}</p>
                <p class="muted">Rows captured in report.csv</p>
            </article>
            <article class="card">
                <h2>Brute-Force Alerts</h2>
                <p class="stat">{{ brute_force_events }}</p>
                <p class="muted">Detected within the active time window</p>
            </article>
            <article class="card">
                <h2>Invalid Users</h2>
                <p class="stat">{{ invalid_user_events }}</p>
                <p class="muted">Suspicious username probes recorded</p>
            </article>
        </section>

        <section class="grid-wide">
            <article class="card">
                <h3>Threat Level Mix</h3>
                <p class="helper">Severity distribution across recorded report events</p>
                <div class="bar-stack" aria-label="Threat level distribution">
                    {% for item in severity_breakdown %}
                    <div class="bar {{ item.css_class }}" style="width: {{ item.width }}%"></div>
                    {% endfor %}
                </div>
                <div class="legend">
                    {% for item in severity_breakdown %}
                    <div class="legend-row">
                        <span class="swatch {{ item.css_class }}"></span>
                        <span>{{ item.label }}</span>
                        <strong>{{ item.count }}</strong>
                    </div>
                    {% endfor %}
                </div>
            </article>

            <article class="card">
                <h3>Threat Status</h3>
                <p class="stat">{{ highest_severity }}</p>
                <p class="muted">Highest severity observed in the current dataset</p>
            </article>
        </section>

        <section class="grid-wide">
            <article class="card">
                <h3>Top Source IPs</h3>
                {% if top_ips %}
                <table>
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Events</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ip, count in top_ips %}
                        <tr>
                            <td>{{ ip }}</td>
                            <td>{{ count }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="muted">No report data yet.</p>
                {% endif %}
            </article>

            <article class="card">
                <h3>Recent Alerts</h3>
                {% if recent_alerts %}
                <ul>
                    {% for alert in recent_alerts %}
                    <li class="alert-item">
                        <div class="alert-top">
                            <span class="badge {{ alert.css_class }}">{{ alert.level }}</span>
                            <span class="alert-time">{{ alert.time }}</span>
                        </div>
                        <p class="alert-text">{{ alert.message }}</p>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <p class="muted">alerts.log is currently empty.</p>
                {% endif %}
            </article>
        </section>
    </main>
</body>
</html>
"""


def load_report_rows():
    if not REPORT_FILE.exists() or REPORT_FILE.stat().st_size == 0:
        return []

    with REPORT_FILE.open("r", encoding="utf-8", newline="") as report_handle:
        reader = csv.DictReader(report_handle)
        return [row for row in reader if row]


def normalize_level(level):
    value = (level or "LOW").strip().upper()
    if value == "ACTION":
        return "HIGH"
    if value in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        return value
    return "LOW"


def severity_css(level):
    return normalize_level(level).lower()


def parse_alert_line(line):
    stripped = line.strip()
    if not stripped:
        return None

    parts = stripped.split("] ", 2)
    if len(parts) < 3:
        return {
            "time": "Unknown",
            "level": "LOW",
            "css_class": "low",
            "message": stripped,
        }

    timestamp = parts[0].lstrip("[")
    level = parts[1].strip("[]")
    normalized = normalize_level(level)
    return {
        "time": timestamp,
        "level": normalized,
        "css_class": severity_css(normalized),
        "message": parts[2],
    }


def load_recent_alerts(limit=5):
    if not ALERT_FILE.exists():
        return []

    with ALERT_FILE.open("r", encoding="utf-8", errors="ignore") as alert_handle:
        alerts = [parse_alert_line(line) for line in alert_handle]

    return [alert for alert in alerts if alert][-limit:][::-1]


def format_last_updated(rows):
    candidate_times = []

    for row in rows:
        raw = row.get("timestamp")
        if not raw:
            continue
        try:
            candidate_times.append(datetime.strptime(raw, "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            continue

    for path in (ALERT_FILE, REPORT_FILE):
        if path.exists():
            candidate_times.append(datetime.fromtimestamp(path.stat().st_mtime))

    if not candidate_times:
        return "No data yet"

    return max(candidate_times).strftime("%Y-%m-%d %H:%M:%S")


def build_severity_breakdown(rows):
    order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    counts = Counter(normalize_level(row.get("severity")) for row in rows if row.get("severity"))
    total = sum(counts.values()) or 1

    return [
        {
            "label": level.title(),
            "count": counts.get(level, 0),
            "width": round((counts.get(level, 0) / total) * 100, 2),
            "css_class": level.lower(),
        }
        for level in order
    ]


def highest_severity(rows):
    order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    seen = [normalize_level(row.get("severity")) for row in rows if row.get("severity")]
    if not seen:
        return "LOW"
    return max(seen, key=lambda level: order[level])


@app.route("/")
def home():
    rows = load_report_rows()
    ip_counter = Counter(row["ip"] for row in rows if row.get("ip"))

    total_events = len(rows)
    brute_force_events = sum(1 for row in rows if row.get("event_type") == "BRUTE_FORCE")
    invalid_user_events = sum(1 for row in rows if row.get("event_type") == "INVALID_USER")

    return render_template_string(
        HTML,
        total_events=total_events,
        brute_force_events=brute_force_events,
        invalid_user_events=invalid_user_events,
        top_ips=ip_counter.most_common(5),
        recent_alerts=load_recent_alerts(),
        last_updated=format_last_updated(rows),
        severity_breakdown=build_severity_breakdown(rows),
        highest_severity=highest_severity(rows),
    )


if __name__ == "__main__":
    app.run(debug=True)
