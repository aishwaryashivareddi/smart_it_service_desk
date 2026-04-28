# Smart IT Service Desk & System Monitoring Automation

A Python-based IT Service Desk automation system developed for TechNova Solutions.  
This project implements ITIL principles to automate ticket management, SLA tracking, system monitoring, logging, reporting, and repeated issue analysis.

---

## Project Structure
```text
smart_it_service_desk/
├── main.py  
├── tickets.py  
├── monitor.py  
├── reports.py  
├── utils.py  
├── logger.py  
├── itil.py  
├── requirements.txt  
├── tests/  
│   └── test_project.py  
├── data/  
│   ├── tickets.json  
│   ├── logs.txt  
│   ├── backup.csv  
│   └── problems.json  
└── README.md  
```
---

## Features

### Ticket Management
- Create Ticket  
- View All Tickets  
- Search Ticket by ID  
- Update Ticket Status  
- Close Ticket  
- Delete Ticket  

---

### Priority Logic

| Issue           | Priority |
|----------------|----------|
| Server Down    | P1       |
| Internet Down  | P2       |
| Laptop Slow    | P3       |
| Password Reset | P4       |

---

### SLA Tracking

| Priority | SLA |
|----------|-----|
| P1 | 1 Hour |
| P2 | 4 Hours |
| P3 | 8 Hours |
| P4 | 24 Hours |

- Detect SLA breaches  
- Generate escalation alerts  

---

### System Monitoring

Monitors:
- CPU Usage  
- RAM Usage  
- Disk Usage  
- Network Usage  

If:
- CPU > 90%  
- RAM > 95%  
- Disk < 10%  

➡ Automatically creates high-priority (P1) ticket  

---

### Reports

- Daily Summary Report  
- Monthly Trend Report  
- Full Report  

Includes:
- Total tickets  
- Open / Closed tickets  
- High priority tickets  
- SLA breaches  
- Most common issues  
- Department analysis  

---

### File Handling

- JSON storage (tickets.json)  
- CSV backup (backup.csv)  
- Logging (logs.txt)  
- Problem tracking (problems.json)  

---

## ITIL Concepts

- Incident Management  
- Service Request Management  
- Problem Management (auto after 5 repeats)  
- Change Management  
- SLA Monitoring  

---

## OOP Concepts

- Classes & Objects  
- Inheritance  
- Encapsulation  
- Polymorphism  
- Static Methods  
- Class Methods  

---

## Testing

Run test cases:

```bash
python -m pytest
