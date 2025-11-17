import time
import os

# Try common Mosquitto log locations
LOG_PATHS = [
    "/opt/homebrew/var/log/mosquitto/mosquitto.log"  # macOS (brew)
]

def find_log_file():
    for path in LOG_PATHS:
        if os.path.exists(path):
            return path
    print("[BROKER] No log file found in known locations.")
    return None

def tail_log(path):
    print(f"[BROKER] Monitoring log file: {path}")
    with open(path, "r") as f:
        # Go to end of file
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                print("[BROKER LOG]", line.strip())  # simple print for now
            time.sleep(0.2)

def main():
    log_path = find_log_file()
    if log_path:
        tail_log(log_path)

if __name__ == "__main__":
    main()
