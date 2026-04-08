PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: install run-ids run-dashboard reset-demo seed-demo

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

run-ids:
	$(PYTHON) log_monitor.py

run-dashboard:
	$(PYTHON) app.py

reset-demo:
	: > alerts.log
	printf 'timestamp,ip,user,event_type,severity\n' > report.csv
	printf '%s\n' \
	'Jul 10 10:00:01 ubuntu sshd[1234]: Failed password for invalid user admin from 192.168.1.10 port 22 ssh2' \
	'Jul 10 10:00:03 ubuntu sshd[1235]: Failed password for root from 192.168.1.10 port 22 ssh2' \
	'Jul 10 10:00:05 ubuntu sshd[1236]: Failed password for test from 192.168.1.10 port 22 ssh2' \
	'Jul 10 10:00:08 ubuntu sshd[1237]: Invalid user guest from 10.0.0.5' > sample_auth.log

seed-demo:
	printf '%s\n' \
	'Jul 10 10:01:01 ubuntu sshd[2001]: Failed password for admin from 8.8.8.8 port 22 ssh2' \
	'Jul 10 10:01:03 ubuntu sshd[2002]: Failed password for admin from 8.8.8.8 port 22 ssh2' \
	'Jul 10 10:01:05 ubuntu sshd[2003]: Failed password for admin from 8.8.8.8 port 22 ssh2' \
	'Jul 10 10:01:08 ubuntu sshd[2004]: Invalid user hacker from 5.5.5.5' >> sample_auth.log
