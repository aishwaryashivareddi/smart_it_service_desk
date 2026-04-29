"""
utils.py - Utility functions for logging, file handling, backup, and SLA configuration.
"""

import json
import csv
import os
from datetime import datetime

# ===== Paths =====
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.json")
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.json")
LOG_FILE = os.path.join(DATA_DIR, "logs.txt")
BACKUP_FILE = os.path.join(DATA_DIR, "backup.csv")

# ===== Priority Mapping (Q2) =====
PRIORITY_MAP = {
    "server down": "P1",
    "internet down": "P2",
    "laptop slow": "P3",
    "password reset": "P4",
    "printer not working": "P3",
    "outlook not opening": "P3",
    "disk space full": "P2",
    "high cpu usage": "P1",
    "application crash": "P2",
}

# ===== SLA Timers in minutes (Q4) =====
SLA_LIMITS = {
    "P1": 60,
    "P2": 240,
    "P3": 480,
    "P4": 1440,
}

# ===== Escalation thresholds in minutes (Q5) =====
ESCALATION_THRESHOLDS = {
    "P1": 30,
    "P2": 120,
}

# ===== System Monitoring Thresholds (Q7) =====
SYSTEM_THRESHOLDS = {
    "cpu_percent": 90,
    "ram_percent": 95,
    "disk_free_percent": 10,
}


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


# ===== Logging (Q9) =====
def log_event(message, level="INFO"):
    """Append a timestamped event to logs.txt with log level."""
    ensure_data_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(entry)
    except Exception as e:
        print(f"Logging error: {e}")        

# ===== JSON File Handling (Q8) =====
def load_tickets():
    """Load tickets from tickets.json. Returns list of dicts."""
    ensure_data_dir()
    try:
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        log_event("tickets.json not found — starting fresh.")
        return []
    except json.JSONDecodeError:
        log_event("ERROR: tickets.json is corrupted — starting fresh.")
        return []


def save_tickets(tickets):
    """Save tickets list to tickets.json."""
    ensure_data_dir()
    try:
        with open(TICKETS_FILE, "w") as f:
            json.dump(tickets, f, indent=2, default=str)
    except Exception as e:
        log_event(f"ERROR saving tickets: {e}")
        raise

def load_problems():
    """Load problem records from problems.json."""
    ensure_data_dir()
    try:
        with open(PROBLEMS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        log_event("problems.json not found — starting fresh.", "WARNING")
        return []
    except json.JSONDecodeError:
        log_event("ERROR: problems.json is corrupted — starting fresh.", "ERROR")
        return []


def save_problems(problems):
    """Save problem records to problems.json."""
    ensure_data_dir()
    try:
        with open(PROBLEMS_FILE, "w") as f:
            json.dump(problems, f, indent=2, default=str)
    except Exception as e:
        log_event(f"ERROR saving problems: {e}", "ERROR")
        raise


def generate_problem_id(problems):
    """Generate next problem ID like PRB-001."""
    if not problems:
        return "PRB-001"

    last_num = max(int(p["problem_id"].split("-")[1]) for p in problems)
    return f"PRB-{last_num + 1:03d}"

# ===== CSV Backup (Q10) =====
def backup_to_csv(tickets):
    """Export all tickets to backup.csv."""
    ensure_data_dir()
    if not tickets:
        log_event("Backup skipped — no tickets to export.")
        return

    # Collect ALL keys across all tickets (handles ProblemRecord extra fields)
    all_keys = set()
    for t in tickets:
        all_keys.update(t.keys())
    headers = sorted(all_keys)
    try:
        with open(BACKUP_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(tickets)
        log_event(f"Backup created: {len(tickets)} tickets exported to backup.csv")
    except Exception as e:
        log_event(f"ERROR creating backup: {e}")
        raise


def assign_priority(description):
    """Auto-assign priority based on issue description keywords (Q2)."""
    desc_lower = description.lower()
    for keyword, priority in PRIORITY_MAP.items():
        if keyword in desc_lower:
            return priority
    return "P3"  # Default priority


def generate_ticket_id(tickets):
    """Generate next ticket ID like TKT-001."""
    if not tickets:
        return "TKT-001"
    last_num = max(int(t["ticket_id"].split("-")[1]) for t in tickets)
    return f"TKT-{last_num + 1:03d}"


def get_valid_input(prompt, allow_empty=False):
    """Get non-empty input from user with validation (Q11)."""
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("  [!] Input cannot be empty. Please try again.")

def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] Executing: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper