"""
reports.py - Report generation module (Q16, Q17).

Class: ReportGenerator
Generates Daily Summary and Monthly Trend reports.
"""

from datetime import datetime
from collections import Counter
from utils import load_tickets, log_event
from tickets import Ticket


class ReportGenerator:
    """Generates daily and monthly reports from ticket data."""

    def __init__(self):
        self.tickets = load_tickets()

    def refresh(self):
        """Reload tickets from file."""
        self.tickets = load_tickets()

    # Q16: Daily Summary Report
    def daily_summary(self):
        self.refresh()
        today = datetime.now().strftime("%Y-%m-%d")
        today_tickets = [t for t in self.tickets if t["created_at"].startswith(today)]

        total = len(today_tickets)
        open_count = sum(1 for t in today_tickets if t["status"] == "Open")
        in_progress = sum(1 for t in today_tickets if t["status"] == "In Progress")
        closed = sum(1 for t in today_tickets if t["status"] == "Closed")
        high_priority = sum(1 for t in today_tickets if t["priority"] in ("P1", "P2"))
        sla_breached = sum(1 for t in today_tickets if t.get("sla_breached"))

        print(f"\n{'=' * 50}")
        print(f"  DAILY SUMMARY REPORT -- {today}")
        print(f"{'=' * 50}")
        print(f"  Total Tickets Raised:    {total}")
        print(f"  Open Tickets:            {open_count}")
        print(f"  In Progress:             {in_progress}")
        print(f"  Closed Tickets:          {closed}")
        print(f"  High Priority (P1/P2):   {high_priority}")
        print(f"  SLA Breached:            {sla_breached}")
        print(f"{'=' * 50}")

        log_event(f"Daily report generated -- Total: {total}, Open: {open_count}, "
                  f"Closed: {closed}, SLA Breached: {sla_breached}")

    # Q17: Monthly Trend Report
    def monthly_trend(self):
        self.refresh()
        now = datetime.now()
        month_str = now.strftime("%Y-%m")
        month_tickets = [t for t in self.tickets if t["created_at"].startswith(month_str)]

        if not month_tickets:
            print(f"\n  No tickets found for {month_str}.")
            return

        # Most common issue
        descriptions = [t["description"].lower().strip() for t in month_tickets]
        issue_counter = Counter(descriptions)
        most_common_issue, most_common_count = issue_counter.most_common(1)[0]

        # Average resolution time (for closed tickets)
        resolution_times = []
        
        for t in month_tickets:
            if t.get("status") == "Closed" and t.get("closed_at"):
                try:
                    created = datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S")
                    closed = datetime.strptime(t["closed_at"], "%Y-%m-%d %H:%M:%S")
                    
                    minutes = (closed -created).total_seconds() / 60 
                    
                    if minutes >= 0:
                        resolution_times.append(minutes)
                        
                except Exception as e:
                    log_event(f"Error calculating resolution time for {t.get('ticket_id')}: {e}", "ERROR")
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0                    

        # Department with most incidents
        dept_counter = Counter(t["department"] for t in month_tickets)
        top_dept, top_dept_count = dept_counter.most_common(1)[0]

        # Ticket type breakdown
        type_counter = Counter(t.get("type", "General") for t in month_tickets)

        print(f"\n{'=' * 55}")
        print(f"  MONTHLY TREND REPORT -- {now.strftime('%B %Y')}")
        print(f"{'=' * 55}")
        print(f"  Total Tickets:              {len(month_tickets)}")
        print(f"  Most Common Issue:          {most_common_issue} ({most_common_count}x)")
        print(f"  Avg Resolution Time:        {avg_resolution:.1f} minutes")
        print(f"  Dept with Most Incidents:   {top_dept} ({top_dept_count} tickets)")
        print(f"\n  Ticket Type Breakdown:")
        for ttype, count in type_counter.most_common():
            print(f"    {ttype:<20} {count}")
        print(f"{'=' * 55}")

        log_event(f"Monthly report generated -- {len(month_tickets)} tickets, "
                  f"top issue: {most_common_issue}, top dept: {top_dept}")

    # Combined report
    def full_report(self):
        self.daily_summary()
        self.monthly_trend()
