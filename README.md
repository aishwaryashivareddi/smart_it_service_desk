# Smart IT Service Desk & System Monitoring Automation

Python-based offline IT support automation system for TechNova Solutions.

## Project Structure

```
smart_it_service_desk/
├── main.py          # Entry point — interactive menu (Q3, Q11, Q12, Q14)
├── tickets.py       # OOP ticket system — Ticket, IncidentTicket, ServiceRequest, ProblemRecord (Q1-Q5, Q13-Q15)
├── monitor.py       # System monitoring — CPU, RAM, Disk (Q6, Q7)
├── reports.py       # Report generation — Daily & Monthly (Q16, Q17)
├── utils.py         # Utilities — logging, file I/O, backup, config (Q8-Q10)
├── data/
│   ├── tickets.json # Ticket storage (Q8)
│   ├── logs.txt     # Event logs (Q9)
│   └── backup.csv   # CSV backup (Q10)
└── README.md
```

## Requirements Mapping

| Question | Feature | File |
|----------|---------|------|
| Q1 | Ticket creation with all fields | tickets.py — `TicketManager.create_ticket()` |
| Q2 | Auto-priority by issue type | utils.py — `PRIORITY_MAP`, `assign_priority()` |
| Q3 | Menu: Create/View/Search/Update/Close/Delete | main.py — menu loop |
| Q4 | SLA timers (P1=1h, P2=4h, P3=8h, P4=24h) | utils.py — `SLA_LIMITS`, tickets.py — `check_sla_breaches()` |
| Q5 | Escalation alerts (P1>30m, P2>2h, SLA breached) | tickets.py — `check_escalations()` |
| Q6 | System monitoring (CPU, RAM, Disk) | monitor.py — `Monitor.display_health()` |
| Q7 | Auto-generate tickets on threshold breach | monitor.py — `Monitor.auto_generate_tickets()` |
| Q8 | JSON file storage | utils.py — `load_tickets()`, `save_tickets()` |
| Q9 | Event logging to logs.txt | utils.py — `log_event()` |
| Q10 | CSV backup | utils.py — `backup_to_csv()` |
| Q11 | Exception handling (FileNotFound, invalid input, wrong ID, empty desc) | main.py — try/except, utils.py — `get_valid_input()` |
| Q12 | Debugging techniques | main.py docstring — breakpoints, variable watch, step execution, error tracing |
| Q13 | OOP: Ticket, IncidentTicket, ServiceRequest, ProblemRecord, Monitor, ReportGenerator | tickets.py, monitor.py, reports.py |
| Q14 | ITIL: Incident, Service Request, Problem, Change Request | tickets.py — class types, main.py — `raise_change_request()` |
| Q15 | Auto Problem Record after 5 repeated issues | tickets.py — `_check_problem_threshold()` |
| Q16 | Daily Summary Report | reports.py — `daily_summary()` |
| Q17 | Monthly Trend Report | reports.py — `monthly_trend()` |

## OOP Concepts (Q13)

| Concept | Where |
|---------|-------|
| Constructors | `Ticket.__init__()`, `ProblemRecord.__init__()`, `Monitor.__init__()` |
| Inheritance | `IncidentTicket(Ticket)`, `ServiceRequest(Ticket)`, `ProblemRecord(Ticket)` |
| Encapsulation | `Ticket._status` private field with `@property` getter/setter |
| Method Overriding | `get_type()` overridden in each subclass |
| Static Methods | `Ticket.format_datetime()`, `Monitor._create_system_ticket()` |
| Class Methods | `Ticket.get_ticket_count()` |

## Debugging Techniques (Q12)

| Technique | Where Used |
|-----------|-----------|
| Breakpoints | Set in `create_ticket()` and `check_sla_breaches()` to inspect ticket state |
| Variable Watch | Watched `priority`, `sla_breached`, `elapsed` during SLA logic debugging |
| Step Execution | Stepped through `_check_problem_threshold()` to verify count reaches 5 |
| Error Tracing | All errors logged to `data/logs.txt` with timestamps for post-mortem |

## How to Run

### Prerequisites
- Python 3.8+ (https://www.python.org/downloads/)
- psutil library (for system monitoring)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/aishwaryashivareddi/smart_it_service_desk.git
cd smart_it_service_desk

# 2. Install dependency
pip install psutil

# 3. Run the application
python main.py
```

### Menu Options
```
 1. Create Ticket          7. Check SLA Breaches      13. Full Report
 2. View All Tickets       8. Escalation Alerts       14. Raise Change Request
 3. Search Ticket by ID    9. System Health            0. Exit
 4. Update Ticket Status  10. Auto-Generate Tickets
 5. Close Ticket          11. Daily Summary
 6. Delete Ticket         12. Monthly Trend
```
