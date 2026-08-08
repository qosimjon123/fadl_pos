# Copyright (c) 2026, FadlTech team and contributors

"""Customer domain events — hook points for future listeners (e.g. CRM sync, audit logging).

No handlers are registered yet; this only standardizes the event names and
payload shape emitted by :mod:`fadl_pos.customer.controller`.
"""

from __future__ import annotations

from fadl_pos.core.events import emit

CUSTOMER_CREATED = "customer.created"
CUSTOMER_UPDATED = "customer.updated"
LOYALTY_REGISTERED = "customer.loyalty_registered"
LOYALTY_UNENROLLED = "customer.loyalty_unenrolled"


def customer_created(*, customer: str, user: str) -> None:
	emit(CUSTOMER_CREATED, customer=customer, user=user)


def customer_updated(*, customer: str, user: str) -> None:
	emit(CUSTOMER_UPDATED, customer=customer, user=user)


def loyalty_registered(*, customer: str, loyalty_program: str, user: str) -> None:
	emit(LOYALTY_REGISTERED, customer=customer, loyalty_program=loyalty_program, user=user)


def loyalty_unenrolled(*, customer: str, user: str) -> None:
	emit(LOYALTY_UNENROLLED, customer=customer, user=user)
