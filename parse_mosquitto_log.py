# parse_mosquitto_log.py
"""
Tail and parse the Mosquitto log file to extract connection attempts and IPs.
Requires mosquitto.conf to be set to log_type all and log_dest file <path>.
"""

import time
import csv
import re
import os

LOG_PATH = r"C:\Program Files\mosquitto\log\mosquitto.log"  # change to where your mosquitto.log is
OUT_CSV = "mosq_events.csv"

# Patterns from Mosquitto log lines, examples:
# 1628497123: New connection from 192.168.1.5:58342.
# 1628497126: Socket error on client <clientid>, disconnecting.
# 1628497130: New client connected from 10.0.0.3 as unknown-client (c1, k60, u'username').

PAT_CONNECT = re.compile(r"New connection from (\d+\.\d+\.\d+\.\d+):(\d+)")
PAT_CLIENT_CONNECTED = re.compile(r"New client connected from (\d+\.\d+\.\d+\.\d+) as (\S+)")
PAT_AUTH_FAIL = re.compile(r"Invalid username or password")  # common phrase

def ensure_csv_header():
    if not os.path.exists(OUT_CSV):
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp","event","ip","port_or_clientid","raw_line"])

def tail_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

def parse_and_save(line):
    ip = None
    info = ""
    if m := PAT_CONNECT.search(line):
        ip = m.group(1)
        port = m.group(2)
        info = f"connect_port:{port}"
        event = "connect"
    elif m := PAT_CLIENT_CONNECTED.search(line):
        ip = m.group(1)
        clientid = m.group(2)
        info = f"clientid:{clientid}"
        event = "client_connected"
    elif PAT_AUTH_FAIL.search(line):
        ip = ""
        event = "auth_fail"
    else:
        return

    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ensure_csv_header()
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([ts, event, ip, info, line.strip()])
    print(f"[mosqlog] {ts} | {event} | {ip} | {info}")

def main():
    if not os.path.exists(LOG_PATH):
        print(f"Log path not found: {LOG_PATH}")
        return
    for ln in tail_file(LOG_PATH):
        parse_and_save(ln)

if __name__ == "__main__":
    main()
