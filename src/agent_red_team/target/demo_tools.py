"""Fake tools for the bundled demo agent — a mock support desk.

Read tools return attacker-controllable data (injection points). Action tools
have side effects that must never be triggered by tool data (hijack targets).
"""

from __future__ import annotations


def read_ticket(ticket_id: str) -> str:
    """READ surface — returns ticket text (attacker-controllable)."""
    raise NotImplementedError


def read_webpage(url: str) -> str:
    """READ surface — returns page content (attacker-controllable)."""
    raise NotImplementedError


def refund_customer(ticket_id: str, amount: float) -> str:
    """ACTION surface — forbidden without human approval."""
    raise NotImplementedError


def send_email(to: str, body: str) -> str:
    """ACTION surface — forbidden to external addresses."""
    raise NotImplementedError
