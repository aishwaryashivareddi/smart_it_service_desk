"""
tickets.py - OOP-based ticket system with ITIL practices.

Classes: Ticket, IncidentTicket, ServiceRequest, ProblemRecord, TicketManager
Demonstrates: Constructors, Inheritance, Encapsulation, Method Overriding, Static/Class methods

ITIL Practices (Q14):
  - Incident Management  -> IncidentTicket
  - Service Request Mgmt -> ServiceRequest
  - Problem Management   -> ProblemRecord (auto-created after 5 repeated issues, Q15)
  - Change Request        -> tracked via category
"""

from datetime import datetime, timedelta
from utils import (
    load_tickets, save_tickets, backup_to_csv, log_event,
    assign_priority, generate_ticket_id, get_valid_input,
    SLA_LIMITS, ESCALATION_THRESHOLDS,
)


# ===== Base Class (Q13) =====
class Ticket:
    """Base ticket class with encapsulation (private _status)."""

    _ticket_count = 0  # Class variable

    def __init__(self, ticket_id, employee, department, description, category, priority):
        self.ticket_id = ticket_id
        self.employee = employee
        self.department = department
        self.description = description
        self.category = category
        self.priority = priority
        self._status = "Open"  # Encapsulated
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.closed_at = None
        self.sla_breached = False
        Ticket._ticket_count += 1

    # Encapsulation: getter/setter for status
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in ("Open", "In Progress", "Closed"):
            raise ValueError(f"Invalid status: {value}")
        self._status = value

    # Method to be overridden by subclasses
    def get_type(self):
        return "General"

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "employee": self.employee,
            "department": self.department,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self._status,
            "created_at": self.created_at,
            "closed_at": self.closed_at,
            "sla_breached": self.sla_breached,
            "type": self.get_type(),
        }

    # Static method
    @staticmethod
    def format_datetime(dt_str):
        """Parse datetime string to datetime object."""
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    # Class method
    @classmethod
    def get_ticket_count(cls):
        return cls._ticket_count

    def __str__(self):
        return (f"[{self.ticket_id}] {self.priority} | {self._status} | "
                f"{self.employee} -- {self.description}")


# ===== Inheritance & Method Overriding (Q13, Q14) =====
class IncidentTicket(Ticket):
    """ITIL Incident Management -- unplanned interruption."""

    def get_type(self):
        return "Incident"


class ServiceRequest(Ticket):
    """ITIL Service Request Management -- standard requests like password reset."""

    def get_type(self):
        return "Service Request"


class ProblemRecord(Ticket):
    """ITIL Problem Management -- root cause of repeated incidents (Q15)."""

    def __init__(self, ticket_id, description, occurrence_count):
        super().__init__(
            ticket_id=ticket_id,
            employee="System",
            department="IT",
            description=f"PROBLEM: {description} (occurred {occurrence_count} times)",
            category="Problem Management",
            priority="P1",
        )
        self.occurrence_count = occurrence_count

    def get_type(self):
        return "Problem Record"

    def to_dict(self):
        d = super().to_dict()
        d["occurrence_count"] = self.occurrence_count
        return d


# ===== Ticket Manager (Q1, Q3, Q4, Q5, Q14, Q15) =====
class TicketManager:
    """Manages all ticket operations, SLA tracking, and ITIL workflows."""

    SERVICE_REQUEST_KEYWORDS = ["password reset", "new account", "access request", "software install"]

    def __init__(self):
        self.tickets = load_tickets()

    def _save(self):
        save_tickets(self.tickets)
        backup_to_csv(self.tickets)

    # Q1, Q2: Create ticket with auto-priority
    def create_ticket(self):
        print("\n-- Create New Ticket --")
        employee = get_valid_input("  Employee Name: ")
        department = get_valid_input("  Department: ")
        description = get_valid_input("  Issue Description: ")
        category = get_valid_input("  Category (e.g. Hardware/Software/Network): ")

        priority = assign_priority(description)
        ticket_id = generate_ticket_id(self.tickets)

        # ITIL: decide ticket type (Q14)
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in self.SERVICE_REQUEST_KEYWORDS):
            ticket = ServiceRequest(ticket_id, employee, department, description, category, priority)
        else:
            ticket = IncidentTicket(ticket_id, employee, department, description, category, priority)

        self.tickets.append(ticket.to_dict())
        self._save()
        log_event(f"Ticket created: {ticket_id} | {priority} | {ticket.get_type()} | {description}")
        print(f"\n  [OK] Ticket {ticket_id} created -- Priority: {priority}, Type: {ticket.get_type()}")

        # Q15: Check for repeated issues -> auto-create Problem Record
        self._check_problem_threshold(description)

    # Q3: View all tickets
    def view_all_tickets(self):
        if not self.tickets:
            print("\n  No tickets found.")
            return
        print(f"\n-- All Tickets ({len(self.tickets)}) --")
        print(f"  {'ID':<10} {'Priority':<8} {'Status':<14} {'Type':<18} {'SLA':<10} {'Employee':<15} Description")
        print("  " + "-" * 100)
        for t in self.tickets:
            sla = "BREACHED" if t.get("sla_breached") else "OK"
            print(f"  {t['ticket_id']:<10} {t['priority']:<8} {t['status']:<14} "
                  f"{t.get('type', 'General'):<18} {sla:<10} {t['employee']:<15} {t['description'][:40]}")

    # Q3: Search by ID
    def search_ticket(self):
        tid = get_valid_input("\n  Enter Ticket ID (e.g. TKT-001): ").upper()
        ticket = self._find_ticket(tid)
        if not ticket:
            print(f"  [!] Ticket {tid} not found.")
            return
        print(f"\n-- Ticket Details --")
        for key, val in ticket.items():
            print(f"  {key:<20}: {val}")

    # Q3: Update status
    def update_ticket_status(self):
        tid = get_valid_input("\n  Enter Ticket ID: ").upper()
        ticket = self._find_ticket(tid)
        if not ticket:
            print(f"  [!] Ticket {tid} not found.")
            return

        print(f"  Current status: {ticket['status']}")
        print("  Options: 1) Open  2) In Progress  3) Closed")
        choice = get_valid_input("  Select new status (1-3): ")

        status_map = {"1": "Open", "2": "In Progress", "3": "Closed"}
        new_status = status_map.get(choice)
        if not new_status:
            print("  [!] Invalid choice.")
            return

        old_status = ticket["status"]
        ticket["status"] = new_status
        if new_status == "Closed":
            ticket["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._save()
        log_event(f"Ticket updated: {tid} | {old_status} -> {new_status}")
        print(f"  [OK] {tid} status updated to {new_status}")

    # Q3: Close ticket
    def close_ticket(self):
        tid = get_valid_input("\n  Enter Ticket ID to close: ").upper()
        ticket = self._find_ticket(tid)
        if not ticket:
            print(f"  [!] Ticket {tid} not found.")
            return
        if ticket["status"] == "Closed":
            print(f"  [!] {tid} is already closed.")
            return

        ticket["status"] = "Closed"
        ticket["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        log_event(f"Ticket closed: {tid}")
        print(f"  [OK] {tid} closed.")

    # Q3: Delete ticket
    def delete_ticket(self):
        tid = get_valid_input("\n  Enter Ticket ID to delete: ").upper()
        ticket = self._find_ticket(tid)
        if not ticket:
            print(f"  [!] Ticket {tid} not found.")
            return

        confirm = input(f"  Delete {tid}? (y/n): ").strip().lower()
        if confirm != "y":
            print("  Cancelled.")
            return

        self.tickets.remove(ticket)
        self._save()
        log_event(f"Ticket deleted: {tid}")
        print(f"  [OK] {tid} deleted.")

    # Q4: Check SLA breaches
    def check_sla_breaches(self):
        print("\n-- SLA Check --")
        now = datetime.now()
        breached_count = 0
        for t in self.tickets:
            if t["status"] == "Closed":
                continue
            created = Ticket.format_datetime(t["created_at"])
            sla_minutes = SLA_LIMITS.get(t["priority"], 480)
            deadline = created + timedelta(minutes=sla_minutes)
            if now > deadline and not t.get("sla_breached"):
                t["sla_breached"] = True
                breached_count += 1
                log_event(f"SLA BREACHED: {t['ticket_id']} | {t['priority']} | {t['description']}")
                print(f"  [ALERT] SLA BREACHED: {t['ticket_id']} ({t['priority']}) -- {t['description'][:50]}")

        if breached_count:
            self._save()
        else:
            print("  [OK] No new SLA breaches.")

    # Q5: Escalation alerts
    def check_escalations(self):
        print("\n-- Escalation Alerts --")
        now = datetime.now()
        alerts = []
        for t in self.tickets:
            if t["status"] == "Closed":
                continue
            created = Ticket.format_datetime(t["created_at"])
            elapsed = (now - created).total_seconds() / 60

            # Escalation for P1 after 30 min, P2 after 2 hours
            threshold = ESCALATION_THRESHOLDS.get(t["priority"])
            if threshold and elapsed > threshold and t["status"] != "Closed":
                alerts.append(f"  [!] ESCALATE {t['ticket_id']} ({t['priority']}) -- "
                              f"unresolved for {int(elapsed)} min -- {t['description'][:40]}")
                log_event(f"ESCALATION: {t['ticket_id']} | {t['priority']} | unresolved {int(elapsed)} min")

            # Any SLA breached ticket
            if t.get("sla_breached"):
                alerts.append(f"  [ALERT] SLA BREACHED {t['ticket_id']} ({t['priority']}) -- {t['description'][:40]}")

        if alerts:
            for a in alerts:
                print(a)
        else:
            print("  [OK] No escalations needed.")

    # Q15: Auto-create Problem Record if same issue occurs 5+ times
    def _check_problem_threshold(self, description):
        desc_lower = description.lower()
        count = sum(1 for t in self.tickets
                    if t["description"].lower() == desc_lower and t.get("type") != "Problem Record")
        if count >= 5:
            existing = any(t for t in self.tickets
                          if t.get("type") == "Problem Record" and desc_lower in t["description"].lower())
            if not existing:
                tid = generate_ticket_id(self.tickets)
                problem = ProblemRecord(tid, description, count)
                self.tickets.append(problem.to_dict())
                self._save()
                log_event(f"PROBLEM RECORD auto-created: {tid} | '{description}' occurred {count} times")
                print(f"\n  [ALERT] PROBLEM RECORD {tid} auto-created -- '{description}' repeated {count} times!")

    def _find_ticket(self, ticket_id):
        for t in self.tickets:
            if t["ticket_id"] == ticket_id:
                return t
        return None
