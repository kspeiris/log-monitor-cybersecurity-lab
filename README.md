# Mini IDS Log Monitor

## Overview
This project is a small Python-based intrusion detection lab built in WSL Ubuntu. It monitors SSH-style authentication logs, detects suspicious login behavior, writes alerts and structured reports, and includes a simple Flask dashboard for visualization.

It is designed as a beginner-friendly mini IDS project that demonstrates:
- log parsing with regular expressions
- brute-force detection using a time window
- severity-based alerting
- CSV reporting
- simulated response actions
- a lightweight web dashboard

## Features
- Detects failed SSH login attempts
- Detects invalid user access attempts
- Identifies brute-force activity from repeated failures
- Assigns severity levels: `MEDIUM`, `HIGH`, `CRITICAL`
- Writes runtime alerts to `alerts.log`
- Writes structured event data to `report.csv`
- Prints an attack summary by source IP
- Simulates an automated response action for demo purposes
- Displays dashboard metrics, recent alerts, severity badges, and threat distribution

## Project Structure
```text
log-monitor/
├── .gitignore
├── Makefile
├── README.md
├── app.py
├── log_monitor.py
├── requirements.txt
└── sample_auth.log
```

## Files
- `log_monitor.py` - main IDS monitor script
- `app.py` - Flask dashboard
- `sample_auth.log` - sample authentication log used for testing
- `requirements.txt` - Python dependencies
- `Makefile` - helper commands for setup, reset, and demo runs
- `alerts.log` - generated runtime alert file
- `report.csv` - generated runtime CSV report

## Requirements
- Python 3.12 or similar
- WSL Ubuntu or Linux environment
- `python3-venv` package installed for virtual environments

## Setup
On Ubuntu/WSL, run:

```bash
sudo apt update
sudo apt install -y python3.12-venv
cd ~/log-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running The IDS
Start the log monitor:

```bash
source .venv/bin/activate
python log_monitor.py
```

You should see:

```text
=== Intrusion Detection System Started ===
Monitoring: sample_auth.log
```

The script watches for newly appended log lines in real time.

## Running The Dashboard
Start the Flask dashboard:

```bash
source .venv/bin/activate
python app.py
```

Open this in your browser:

```text
http://127.0.0.1:5000
```

## Demo Workflow
Use one terminal for the IDS:

```bash
source .venv/bin/activate
make reset-demo
make run-ids
```

Use a second terminal to append attack data:

```bash
source .venv/bin/activate
make seed-demo
```

Use a third terminal for the dashboard:

```bash
source .venv/bin/activate
make run-dashboard
```

## Example Test Logs
These sample lines simulate failed login and invalid user attacks:

```text
Jul 10 10:01:01 ubuntu sshd[2001]: Failed password for admin from 8.8.8.8 port 22 ssh2
Jul 10 10:01:03 ubuntu sshd[2002]: Failed password for admin from 8.8.8.8 port 22 ssh2
Jul 10 10:01:05 ubuntu sshd[2003]: Failed password for admin from 8.8.8.8 port 22 ssh2
Jul 10 10:01:08 ubuntu sshd[2004]: Invalid user hacker from 5.5.5.5
```

## Detection Logic
The monitor looks for two main patterns:
- failed password attempts
- invalid usernames

For failed logins:
- each source IP is tracked
- attempts are stored within a 60-second window
- if an IP reaches 3 or more attempts within that window, it is flagged as brute-force activity

Severity levels:
- `MEDIUM` for lower-level suspicious activity
- `HIGH` for repeated brute-force attempts
- `CRITICAL` for heavier repeated attack activity

## Dashboard Contents
The dashboard shows:
- total detected events
- brute-force alert count
- invalid user count
- top source IPs
- recent alerts
- severity badges with colors
- last updated timestamp
- threat-level distribution bar

## Helper Commands
The included `Makefile` provides:

```bash
make install
make reset-demo
make run-ids
make run-dashboard
make seed-demo
```

What they do:
- `make install` - create `.venv` and install dependencies
- `make reset-demo` - clear old generated files and restore starter sample logs
- `make run-ids` - run the IDS monitor
- `make run-dashboard` - run the Flask dashboard
- `make seed-demo` - append demo attack lines to the sample log

## Output Files
These files are generated while the project runs:

### `alerts.log`
Contains human-readable alerts and simulated response actions.

Example:

```text
[2026-04-08 17:01:03] [HIGH] Brute-force detected from 8.8.8.8
[2026-04-08 17:01:03] [ACTION] Would block IP: 8.8.8.8
[2026-04-08 17:01:03] [MEDIUM] Invalid user 'hacker' from 5.5.5.5
```

### `report.csv`
Contains structured event records for analysis and dashboard use.

Example:

```csv
timestamp,ip,user,event_type,severity
2026-04-08 17:01:03,8.8.8.8,admin,FAILED_LOGIN,MEDIUM
2026-04-08 17:01:03,8.8.8.8,admin,FAILED_LOGIN,MEDIUM
2026-04-08 17:01:03,8.8.8.8,admin,FAILED_LOGIN,HIGH
2026-04-08 17:01:03,8.8.8.8,admin,BRUTE_FORCE,HIGH
2026-04-08 17:01:03,5.5.5.5,hacker,INVALID_USER,MEDIUM
```

## Notes
- This project uses `sample_auth.log` for safe testing.
- You can later change the log source to `/var/log/auth.log` on a Linux machine.
- The response action is intentionally a mock action for demo safety.
- `alerts.log` and `report.csv` are ignored by git because they are runtime-generated files.

## Possible Future Improvements
- auto-refreshing dashboard
- charts with JavaScript
- email or Telegram alerting
- support for more log patterns
- real firewall integration on a full Linux server
- unit tests for parsing and detection logic

## Author
Mini IDS project built for learning and demo purposes using Python, WSL Ubuntu, and Flask.
