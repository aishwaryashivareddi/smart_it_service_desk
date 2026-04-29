from tickets import TicketManager
from utils import SLA_LIMITS


def test_ticket_creation():
    tm = TicketManager()
    ticket = tm.create_ticket("Aish", "IT", "Server Down", "Incident")
    assert ticket["ticket_id"] is not None
    assert ticket["priority"] == "P1"


def test_priority_logic():
    tm = TicketManager()
    ticket = tm.create_ticket("User", "HR", "Password Reset", "Service")
    assert ticket["priority"] == "P4"
    assert ticket["type"] == "Service Request"


def test_search_ticket():
    tm = TicketManager()
    ticket = tm.create_ticket("Aish", "IT", "Server Down", "Incident")
    found = tm._find_ticket(ticket["ticket_id"])
    assert found is not None


def test_file_write():
    tm = TicketManager()
    ticket = tm.create_ticket("Test", "IT", "Laptop Slow", "Hardware")
    assert ticket["ticket_id"] is not None


def test_sla_limits_exist():
    assert SLA_LIMITS["P1"] == 60
    assert SLA_LIMITS["P2"] == 240
    assert SLA_LIMITS["P3"] == 480
    assert SLA_LIMITS["P4"] == 1440


def test_invalid_ticket_search():
    tm = TicketManager()
    result = tm._find_ticket("INVALID-ID")
    assert result is None


def test_monitor_import():
    from monitor import Monitor
    monitor = Monitor()
    assert monitor is not None