"""
main.py - Entry point for Smart IT Service Desk.

Provides interactive menu for all operations (Q3).
Handles exceptions for invalid input, wrong IDs, file errors (Q11).

ITIL Change Request Tracking (Q14):
  Change requests are logged as tickets with category "Change Request".

Debugging Techniques Used (Q12):
  - Breakpoints: Set in create_ticket() and check_sla_breaches() during dev
  - Variable watch: Watched 'priority', 'sla_breached', 'elapsed' variables in debugger
  - Step execution: Stepped through _check_problem_threshold() to verify count logic
  - Error tracing: All errors logged to logs.txt with timestamps for post-mortem analysis
"""

from tickets import TicketManager
from monitor import Monitor
from reports import ReportGenerator
from utils import log_event


def print_menu():
    print("""
+==================================================+
|     Smart IT Service Desk -- TechNova            |
+==================================================+
|  TICKET MANAGEMENT                               |
|   1.  Create Ticket                              |
|   2.  View All Tickets                           |
|   3.  Search Ticket by ID                        |
|   4.  Update Ticket Status                       |
|   5.  Close Ticket                               |
|   6.  Delete Ticket                              |
|  SLA & ESCALATION                                |
|   7.  Check SLA Breaches                         |
|   8.  Check Escalation Alerts                    |
|  SYSTEM MONITORING                               |
|   9.  View System Health                         |
|  10.  Auto-Generate Tickets (Threshold Check)    |
|  REPORTS                                         |
|  11.  Daily Summary Report                       |
|  12.  Monthly Trend Report                       |
|  13.  Full Report (Daily + Monthly)              |
|  ITIL                                            |
|  14.  Raise Change Request                       |
|                                                  |
|   0.  Exit                                       |
+==================================================+""")


def raise_change_request(manager):
    """ITIL Change Request Tracking (Q14)."""
    print("\n-- Raise Change Request --")
    from utils import get_valid_input, generate_ticket_id
    from datetime import datetime

    employee = get_valid_input("  Requester Name: ")
    department = get_valid_input("  Department: ")
    description = get_valid_input("  Change Description: ")
    reason = get_valid_input("  Reason for Change: ")

    tid = generate_ticket_id(manager.tickets)
    ticket = {
        "ticket_id": tid,
        "employee": employee,
        "department": department,
        "description": f"[CHANGE REQUEST] {description} | Reason: {reason}",
        "category": "Change Request",
        "priority": "P3",
        "status": "Open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "closed_at": None,
        "sla_breached": False,
        "type": "Change Request",
    }
    manager.tickets.append(ticket)
    manager._save()
    log_event(f"Change Request created: {tid} | {description}")
    print(f"\n  [OK] Change Request {tid} raised successfully.")


def main():
    log_event("Application started.")
    manager = TicketManager()
    monitor = Monitor()
    reporter = ReportGenerator()

    while True:
        print_menu()
        try:
            choice = input("\n  Enter choice (0-14): ").strip()

            if choice == "1":
                manager.create_ticket()
            elif choice == "2":
                manager.view_all_tickets()
            elif choice == "3":
                manager.search_ticket()
            elif choice == "4":
                manager.update_ticket_status()
            elif choice == "5":
                manager.close_ticket()
            elif choice == "6":
                manager.delete_ticket()
            elif choice == "7":
                manager.check_sla_breaches()
            elif choice == "8":
                manager.check_escalations()
            elif choice == "9":
                monitor.display_health()
            elif choice == "10":
                updated = monitor.auto_generate_tickets()
                if updated is not None:
                    manager.tickets = updated
            elif choice == "11":
                reporter.daily_summary()
            elif choice == "12":
                reporter.monthly_trend()
            elif choice == "13":
                reporter.full_report()
            elif choice == "14":
                raise_change_request(manager)
            elif choice == "0":
                log_event("Application exited.")
                print("\n  Goodbye!")
                break
            else:
                print("  [!] Invalid choice. Please enter 0-14.")
                log_event(f"Invalid menu input: '{choice}'")

        except KeyboardInterrupt:
            log_event("Application interrupted by user.")
            print("\n\n  Application interrupted. Goodbye!")
            break
        except ValueError as e:
            print(f"  [!] Input error: {e}")
            log_event(f"ValueError: {e}")
        except FileNotFoundError as e:
            print(f"  [!] File error: {e}")
            log_event(f"FileNotFoundError: {e}")
        except Exception as e:
            print(f"  [!] Unexpected error: {e}")
            log_event(f"ERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
