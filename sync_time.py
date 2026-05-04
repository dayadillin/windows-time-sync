# sync_time.py
#
# I dual boot Ubuntu and Windows on my laptop.
# Every time I log into Windows, the clock is wrong because
# Ubuntu keeps the hardware clock in UTC but Windows expects local time.
#
# Instead of manually clicking the sync button every single time,
# I wrote this script to do it automatically on login via Task Scheduler.
#
# Requests admin elevation on its own if not already running as admin.

import subprocess
import sys
import ctypes
import logging
import time
from datetime import datetime
from pathlib import Path


# log file sits right next to this script
LOG_FILE = Path(__file__).parent / "sync_time.log"
LOG_MAX_LINES = 200  # don't let the log file grow forever


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def elevate():
    # re-launch this script as admin using the runas verb
    # this triggers the UAC prompt so Windows asks for permission
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([f'"{sys.argv[0]}"'] + sys.argv[1:]), None, 0
    )
    sys.exit(0)


def trim_log(path: Path, max_lines: int):
    # keep only the last N lines so the log doesn't pile up over time
    try:
        if path.exists():
            lines = path.read_text(encoding="utf-8").splitlines()
            if len(lines) > max_lines:
                path.write_text("\n".join(lines[-max_lines:]) + "\n", encoding="utf-8")
    except Exception:
        pass


def sync_time():
    # if not admin, re-launch with elevation and exit this instance
    if not is_admin():
        elevate()
        return

    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    trim_log(LOG_FILE, LOG_MAX_LINES)
    logging.info("--- sync started ---")

    # register w32tm just in case (harmless if already registered)
    subprocess.run(["w32tm", "/register"], capture_output=True, text=True)

    # make sure the Windows Time service is actually running
    subprocess.run(["net", "start", "w32tm"], capture_output=True, text=True)

    # wait a moment for the service to fully start before syncing
    time.sleep(3)

    # the actual sync
    result = subprocess.run(
        ["w32tm", "/resync", "/force"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        logging.info(f"sync ok: {result.stdout.strip()}")
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] time synced successfully")
    else:
        logging.warning(f"something went wrong (code {result.returncode})")
        logging.warning(f"stdout: {result.stdout.strip()}")
        logging.warning(f"stderr: {result.stderr.strip()}")
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] sync failed, check {LOG_FILE}")

    logging.info("--- sync finished ---\n")


if __name__ == "__main__":
    sync_time()
