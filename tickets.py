"""
tickets.py - OOP-based ticket system with ITIL practices.
"""

from datetime import datetime, timedelta
from utils import (
    load_tickets,
    save_tickets,
    backup_to_csv,
    log_event,
    assign_priority,
    generate_ticket_id,
    get_valid_input,
    SLA_LIMITS,
    ESCALATION_THRESHOLDS,
    log_decorator,
)


class Ticket:
    """Base ticket class."""

    _ticket_count = 0

    def __init__(self, ticket_id, employee, department, description, category, priority):
        self.ticket_id = ticket_id
        self.employee = employee
        self.department = department
        self.description = description
        self.category = category
        self.priority = priority
        self._status = "Open"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.closed_at = None
        self.sla_breached = False
        Ticket._ticket_count += 1

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in ("Open", "In Progress", "Closed"):
            raise ValueError(f"Invalid status: {value}")
        self._status = value

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

    @staticmethod
    def format_datetime(dt_str):
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

    @classmethod
    def get_ticket_count(cls):
        return cls._ticket_count

    def __str__(self):
        return (
            f"[{self.ticket_id}] {self.priority} | "
            f"{self._status} | {self.employee} -- {self.description}"
        )


class IncidentTicket(Ticket):
    """ITIL Incident Management."""

    def get_type(self):
        return "Incident"


class ServiceRequest(Ticket):
    """ITIL Service Request Management."""

    def get_type(self):
        return "Service Request"


class ProblemRecord(Ticket):
    """ITIL Problem Management."""

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
        data = super().to_dict()
        data["occurrence_count"] = self.occurrence_count
        return data


class TicketManager:
    """Manages ticket operations, SLA tracking, and ITIL workflows."""

    SERVICE_REQUEST_KEYWORDS = [
        "password reset",
        "new account",
        "access request",
        "software install",
    ]

    def __init__(self):
        self.tickets = load_tickets()

    def _save(self):
        save_tickets(self.tickets)
        backup_to_csv(self.tickets)

    # Create ticket
    @log_decorator
    def create_ticket(self, employee=None, department=None, description=None, category=None):
        print("\n-- Create New Ticket --")

        if employee is None:
            employee = get_valid_input("  Employee Name: ")

        if department is None:
            department = get_valid_input("  Department: ")

        if description is None:
            description = get_valid_input("  Issue Description: ")

        if category is None:
            category = get_valid_input("  Category (e.g. Hardware/Software/Network): ")

        priority = assign_priority(description)
        ticket_id = generate_ticket_id(self.tickets)

        desc_lower = description.lower()

        if any(keyword in desc_lower for keyword in self.SERVICE_REQUEST_KEYWORDS):
            ticket = ServiceRequest(
                ticket_id, employee, department, description, category, priority
            )
        else:
            ticket = IncidentTicket(
                ticket_id, employee, department, description, category, priority
            )

        ticket_dict = ticket.to_dict()
        self.tickets.append(ticket_dict)
        self._save()

        log_event(
            f"Ticket created: {ticket_id} | {priority} | "
            f"{ticket.get_type()} | {description}"
        )

        print(
            f"\n  [OK] Ticket {ticket_id} created -- "
            f"Priority: {priority}, Type: {ticket.get_type()}"
        )

        self._check_problem_threshold(description)

        return ticket_dict

    # View all tickets
    def view_all_tickets(self):
        if not self.tickets:
            print("\n  No tickets found.")
            return

        print(f"\n-- All Tickets ({len(self.tickets)}) --")
        print(
            f"  {'ID':<10} {'Priority':<8} {'Status':<14} "
            f"{'Type':<18} {'SLA':<10} {'Employee':<20} Description"
        )
        print("  " + "-" * 110)

        for ticket in self.tickets:
            sla = "BREACHED" if ticket.get("sla_breached") else "OK"
            print(
                f"  {ticket['ticket_id']:<10} "
                f"{ticket['priority']:<8} "
                f"{ticket['status']:<14} "
                f"{ticket.get('type', 'General'):<18} "
                f"{sla:<10} "
                f"{ticket['employee']:<20} "
                f"{ticket['description'][:40]}"
            )

    # Search ticket
    def search_ticket(self):
        ticket_id = get_valid_input("\n  Enter Ticket ID (e.g. TKT-001): ").upper()
        ticket = self._find_ticket(ticket_id)

        if not ticket:
            print(f"  [!] Ticket {ticket_id} not found.")
            return

        print("\n-- Ticket Details --")
        for key, value in ticket.items():
            print(f"  {key:<20}: {value}")

    # Update ticket status
    def update_ticket_status(self):
        ticket_id = get_valid_input("\n  Enter Ticket ID: ").upper()
        ticket = self._find_ticket(ticket_id)

        if not ticket:
            print(f"  [!] Ticket {ticket_id} not found.")
            return

        print(f"  Current status: {ticket['status']}")
        print("  Options: 1) Open  2) In Progress  3) Closed")

        choice = get_valid_input("  Select new status (1-3): ")

        status_map = {
            "1": "Open",
            "2": "In Progress",
            "3": "Closed",
        }

        new_status = status_map.get(choice)

        if not new_status:
            print("  [!] Invalid choice.")
            return

        old_status = ticket["status"]
        ticket["status"] = new_status

        if new_status == "Closed":
            ticket["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._save()
        log_event(f"Ticket updated: {ticket_id} | {old_status} -> {new_status}")

        print(f"  [OK] {ticket_id} status updated to {new_status}")

    # Close ticket
    def close_ticket(self):
        ticket_id = get_valid_input("\n  Enter Ticket ID to close: ").upper()
        ticket = self._find_ticket(ticket_id)

        if not ticket:
            print(f"  [!] Ticket {ticket_id} not found.")
            return

        if ticket["status"] == "Closed":
            print(f"  [!] {ticket_id} is already closed.")
            return

        ticket["status"] = "Closed"
        ticket["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._save()
        log_event(f"Ticket closed: {ticket_id}")

        print(f"  [OK] {ticket_id} closed.")

    # Delete ticket
    def delete_ticket(self):
        ticket_id = get_valid_input("\n  Enter Ticket ID to delete: ").upper()
        ticket = self._find_ticket(ticket_id)

        if not ticket:
            print(f"  [!] Ticket {ticket_id} not found.")
            return

        confirm = input(f"  Delete {ticket_id}? (y/n): ").strip().lower()

        if confirm != "y":
            print("  Cancelled.")
            return

        self.tickets.remove(ticket)
        self._save()
        log_event(f"Ticket deleted: {ticket_id}")

        print(f"  [OK] {ticket_id} deleted.")

    # SLA breach check
    def check_sla_breaches(self):
        print("\n-- SLA Check --")

        now = datetime.now()
        breached_count = 0

        for ticket in self.tickets:
            if ticket["status"] == "Closed":
                continue

            created = Ticket.format_datetime(ticket["created_at"])
            sla_minutes = SLA_LIMITS.get(ticket["priority"], 480)
            deadline = created + timedelta(minutes=sla_minutes)

            if now > deadline and not ticket.get("sla_breached"):
                ticket["sla_breached"] = True
                breached_count += 1

                log_event(
                    f"SLA BREACHED: {ticket['ticket_id']} | "
                    f"{ticket['priority']} | {ticket['description']}"
                )

                print(
                    f"  [ALERT] SLA BREACHED: {ticket['ticket_id']} "
                    f"({ticket['priority']}) -- {ticket['description'][:50]}"
                )

        if breached_count:
            self._save()
        else:
            print("  [OK] No new SLA breaches.")

    # Escalation check
    def check_escalations(self):
        print("\n-- Escalation Alerts --")

        now = datetime.now()
        alerts = []

        for ticket in self.tickets:
            if ticket["status"] == "Closed":
                continue

            created = Ticket.format_datetime(ticket["created_at"])
            elapsed = (now - created).total_seconds() / 60

            threshold = ESCALATION_THRESHOLDS.get(ticket["priority"])

            if threshold and elapsed > threshold:
                alerts.append(
                    f"  [!] ESCALATE {ticket['ticket_id']} "
                    f"({ticket['priority']}) -- unresolved for "
                    f"{int(elapsed)} min -- {ticket['description'][:40]}"
                )

                log_event(
                    f"ESCALATION: {ticket['ticket_id']} | "
                    f"{ticket['priority']} | unresolved {int(elapsed)} min"
                )

            if ticket.get("sla_breached"):
                alerts.append(
                    f"  [ALERT] SLA BREACHED {ticket['ticket_id']} "
                    f"({ticket['priority']}) -- {ticket['description'][:40]}"
                )

        if alerts:
            for alert in alerts:
                print(alert)
        else:
            print("  [OK] No escalations needed.")

    # Problem management
    def _check_problem_threshold(self, description):
        desc_lower = description.lower()

        count = sum(
            1
            for ticket in self.tickets
            if ticket["description"].lower() == desc_lower
            and ticket.get("type") != "Problem Record"
        )

        if count >= 5:
            existing = any(
                ticket
                for ticket in self.tickets
                if ticket.get("type") == "Problem Record"
                and desc_lower in ticket["description"].lower()
            )

            if not existing:
                ticket_id = generate_ticket_id(self.tickets)
                problem = ProblemRecord(ticket_id, description, count)

                self.tickets.append(problem.to_dict())
                self._save()

                log_event(
                    f"PROBLEM RECORD auto-created: {ticket_id} | "
                    f"'{description}' occurred {count} times"
                )

                print(
                    f"\n  [ALERT] PROBLEM RECORD {ticket_id} auto-created -- "
                    f"'{description}' repeated {count} times!"
                )

    def _find_ticket(self, ticket_id):
        for ticket in self.tickets:
            if ticket["ticket_id"] == ticket_id:
                return ticket
        return None