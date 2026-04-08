import csv
import re
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("sample_auth.log")  # change to /var/log/auth.log later
ALERT_FILE = Path("alerts.log")
REPORT_FILE = Path("report.csv")

FAILED_LOGIN_THRESHOLD = 3
TIME_WINDOW = 60

failed_login_pattern = re.compile(
    r"Failed password for (invalid user )?(?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)"
)

invalid_user_pattern = re.compile(
    r"Invalid user (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)"
)

recent_attempts = defaultdict(deque)
attack_counts = defaultdict(int)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_report_file():
    if REPORT_FILE.exists() and REPORT_FILE.stat().st_size > 0:
        return

    with REPORT_FILE.open("w", newline="", encoding="utf-8") as report_handle:
        writer = csv.writer(report_handle)
        writer.writerow(["timestamp", "ip", "user", "event_type", "severity"])


def get_severity(attempt_count):
    if attempt_count >= 5:
        return "CRITICAL"
    if attempt_count >= 3:
        return "HIGH"
    return "MEDIUM"


def send_alert(message, level="LOW"):
    alert = f"[{timestamp()}] [{level}] {message}"
    print(alert)

    with ALERT_FILE.open("a", encoding="utf-8") as alert_handle:
        alert_handle.write(alert + "\n")


def write_report(ip, user, event_type, level):
    ensure_report_file()

    with REPORT_FILE.open("a", newline="", encoding="utf-8") as report_handle:
        writer = csv.writer(report_handle)
        writer.writerow([timestamp(), ip, user, event_type, level])


def print_summary():
    print("\n=== Attack Summary ===")
    if not attack_counts:
        print("No attacks recorded yet.")
        return

    for ip, count in sorted(attack_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"{ip} -> {count} attempts")


def respond_to_attack(ip):
    action = f"[{timestamp()}] [ACTION] Would block IP: {ip}"
    print(action)

    with ALERT_FILE.open("a", encoding="utf-8") as alert_handle:
        alert_handle.write(action + "\n")


def process_line(line):
    now = time.time()

    failed = failed_login_pattern.search(line)
    if failed:
        user = failed.group("user")
        ip = failed.group("ip")

        attack_counts[ip] += 1
        recent_attempts[ip].append(now)

        while recent_attempts[ip] and now - recent_attempts[ip][0] > TIME_WINDOW:
            recent_attempts[ip].popleft()

        print(
            f"[{timestamp()}] Failed login -> User: {user} | IP: {ip} | Count: {attack_counts[ip]}"
        )
        write_report(ip, user, "FAILED_LOGIN", get_severity(len(recent_attempts[ip])))

        if len(recent_attempts[ip]) >= FAILED_LOGIN_THRESHOLD:
            severity = get_severity(len(recent_attempts[ip]))
            send_alert(f"Brute-force detected from {ip}", severity)
            write_report(ip, user, "BRUTE_FORCE", severity)
            print_summary()
            respond_to_attack(ip)
        return

    invalid = invalid_user_pattern.search(line)
    if invalid:
        user = invalid.group("user")
        ip = invalid.group("ip")

        attack_counts[ip] += 1
        print(f"[{timestamp()}] Invalid user -> User: {user} | IP: {ip}")
        send_alert(f"Invalid user '{user}' from {ip}", "MEDIUM")
        write_report(ip, user, "INVALID_USER", "MEDIUM")


def monitor_logs():
    LOG_FILE.touch(exist_ok=True)
    ALERT_FILE.touch(exist_ok=True)
    ensure_report_file()

    print("=== Intrusion Detection System Started ===")
    print(f"Monitoring: {LOG_FILE}")

    with LOG_FILE.open("r", encoding="utf-8", errors="ignore") as log_handle:
        log_handle.seek(0, 2)

        while True:
            line = log_handle.readline()
            if not line:
                time.sleep(0.5)
                continue

            process_line(line)


if __name__ == "__main__":
    monitor_logs()
