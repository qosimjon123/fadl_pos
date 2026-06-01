# Copyright (c) 2026, FadlTech team and contributors
"""Typed API contracts for POS session (shift) RPC and responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import NotRequired, TypedDict


class BalanceDetailItem(TypedDict):
	mode_of_payment: str
	opening_amount: float


class OpenShiftRequest(TypedDict):
	"""Logical open-shift payload after JSON parse."""

	pos_profile: str
	company: str
	balance_details: list[BalanceDetailItem]


class ClosingReconciliationItem(TypedDict):
	mode_of_payment: str
	closing_amount: float


class CloseShiftResponse(TypedDict, total=False):
	status: str
	closing_entry: str
	is_final: bool
	entry_status: str
	error_message: str | None
	message: str


# --- Internal Types (used within services) ---


class InternalPaymentMethod(TypedDict):
	pos_profile: str
	mode_of_payment: str
	default: int
	mop_type: str


# --- API Response Serializers ---


class ChecklistItem(TypedDict):
	title: str


class Checklists(TypedDict):
	opening: list[ChecklistItem]
	closing: list[ChecklistItem]


class PaymentMethodSerializer(TypedDict):
	name: str
	default: int
	type: str  # ERPNext Mode of Payment type (e.g. Cash); required_ob True iff Cash
	required_ob: bool


class PosProfileResponseSerializer(TypedDict):
	name: str
	status: str
	company: str
	opening_entry: str | None
	# Present when status is Open (early return from get_list)
	opening_entry_date: NotRequired[datetime | date | None]
	checklists: NotRequired[list[Checklists]]
	payment_methods: NotRequired[list[PaymentMethodSerializer]]


class SessionListResponseSerializer(TypedDict):
	pos_profiles: list[PosProfileResponseSerializer]
