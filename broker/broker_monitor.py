import time
import os

LOG_FILE = "/opt/homebrew/var/log/mosquitto/mosquitto.log"

def tail_log(path):
    print("[BROKER] Monitoring log file:", path)
    with open(path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                print("[BROKER LOG]", line.strip())
            time.sleep(0.1)

def main():
    if not os.path.exists(LOG_FILE):
        print("[BROKER] Log file not found:", LOG_FILE)
        return
    tail_log(LOG_FILE)

if __name__ == "__main__":
    main()
