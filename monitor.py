"""
monitor.py - System monitoring module (Q6, Q7).

Class: Monitor
Monitors CPU, RAM, Disk usage and auto-generates tickets when thresholds are exceeded.
"""

import platform
from datetime import datetime
from utils import (
    log_event, generate_ticket_id, save_tickets, backup_to_csv,
    load_tickets, SYSTEM_THRESHOLDS,
)

# Try importing psutil; provide fallback if not installed
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class Monitor:
    """System health monitor with auto-ticket generation (Q6, Q7)."""

    def __init__(self):
        self._cpu = 0.0
        self._ram = 0.0
        self._disk = 0.0
        self._disk_free = 0.0

    # Encapsulation: read-only properties
    @property
    def cpu(self):
        return self._cpu

    @property
    def ram(self):
        return self._ram

    @property
    def disk_free(self):
        return self._disk_free

    def collect_metrics(self):
        """Collect current system metrics (Q6)."""
        if not PSUTIL_AVAILABLE:
            print("  WARNING: psutil not installed. Install with: pip install psutil")
            return False

        self._cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        self._ram = mem.percent
        disk = psutil.disk_usage("/")
        self._disk = disk.percent
        self._disk_free = 100 - disk.percent
        return True

    def display_health(self):
        """Display current system health (Q6)."""
        print("\n-- System Health --")
        if not self.collect_metrics():
            return

        cpu_status = "[CRITICAL]" if self._cpu > SYSTEM_THRESHOLDS["cpu_percent"] else "[OK]"
        ram_status = "[CRITICAL]" if self._ram > SYSTEM_THRESHOLDS["ram_percent"] else "[OK]"
        disk_status = "[CRITICAL]" if self._disk_free < SYSTEM_THRESHOLDS["disk_free_percent"] else "[OK]"

        print(f"  CPU Usage:       {self._cpu:>6.1f}%  {cpu_status}")
        print(f"  RAM Usage:       {self._ram:>6.1f}%  {ram_status}")
        print(f"  Disk Used:       {self._disk:>6.1f}%  (Free: {self._disk_free:.1f}%)  {disk_status}")
        print(f"  Platform:        {platform.system()} {platform.release()}")

        log_event(f"System check — CPU: {self._cpu}%, RAM: {self._ram}%, Disk Free: {self._disk_free:.1f}%")

    def auto_generate_tickets(self):
        """Auto-generate high-priority tickets if thresholds exceeded (Q7)."""
        if not PSUTIL_AVAILABLE:
            print("  WARNING: psutil not installed - cannot monitor.")
            return

        self.collect_metrics()
        tickets = load_tickets()
        generated = []

        if self._cpu > SYSTEM_THRESHOLDS["cpu_percent"]:
            generated.append(self._create_system_ticket(
                tickets, f"High CPU usage detected: {self._cpu}%", "P1"))

        if self._ram > SYSTEM_THRESHOLDS["ram_percent"]:
            generated.append(self._create_system_ticket(
                tickets, f"High RAM usage detected: {self._ram}%", "P1"))

        if self._disk_free < SYSTEM_THRESHOLDS["disk_free_percent"]:
            generated.append(self._create_system_ticket(
                tickets, f"Disk space critically low: {self._disk_free:.1f}% free", "P1"))

        if generated:
            save_tickets(tickets)
            backup_to_csv(tickets)
            for tid in generated:
                print(f"  [ALERT] Auto-ticket created: {tid}")
            # Return the updated tickets so caller can sync
            return tickets
        else:
            print("  [OK] All system metrics within normal range.")
            return None

    @staticmethod
    def _create_system_ticket(tickets, description, priority):
        """Create a system-generated ticket and append to tickets list."""
        tid = generate_ticket_id(tickets)
        ticket = {
            "ticket_id": tid,
            "employee": "System Monitor",
            "department": "IT Infrastructure",
            "description": description,
            "category": "System Alert",
            "priority": priority,
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "closed_at": None,
            "sla_breached": False,
            "type": "Incident",
        }
        tickets.append(ticket)
        log_event(f"AUTO-TICKET: {tid} | {priority} | {description}")
        return tid
