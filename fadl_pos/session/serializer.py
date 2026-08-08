# Copyright (c) 2026, FadlTech team and contributors

"""Pydantic v2 schemas for the POS shift session RPC (list / open / close)."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from pydantic import Field, field_validator

from fadl_pos.core.serializer import InputSchema, OutputSchema

__all__ = [
	"BalanceDetailItem",
	"ChecklistItem",
	"Checklists",
	"CloseShiftIn",
	"CloseShiftOut",
	"ClosingReconciliationItem",
	"OpenShiftIn",
	"PaymentMethodOut",
	"PosProfileOut",
	"SessionListEnvelopeOut",
	"SessionListIn",
	"SessionListOut",
]


class BalanceDetailItem(InputSchema):
	name: str = Field(min_length=1)
	opening_amount: float


class ClosingReconciliationItem(InputSchema):
	name: str = Field(min_length=1)
	closing_amount: float


class SessionListIn(InputSchema):
	pass


class OpenShiftIn(InputSchema):
	pos_profile: str = Field(min_length=1)
	company: str = Field(min_length=1)
	comment: str | None = None
	balance_details: list[BalanceDetailItem] = Field(default_factory=list)

	@field_validator("balance_details", mode="before")
	@classmethod
	def coerce_balance_details(cls, value: Any) -> Any:
		if value is None or (isinstance(value, str) and not value.strip()):
			return []
		if isinstance(value, str):
			return json.loads(value)
		return value


class CloseShiftIn(InputSchema):
	opening_entry_name: str = Field(min_length=1)
	comment: str | None = None
	closing_data: list[ClosingReconciliationItem] | None = None

	@field_validator("closing_data", mode="before")
	@classmethod
	def coerce_closing_data(cls, value: Any) -> Any:
		if value is None or (isinstance(value, str) and not value.strip()):
			return None
		if isinstance(value, str):
			return json.loads(value)
		return value


class ChecklistItem(OutputSchema):
	title: str


class Checklists(OutputSchema):
	opening: list[ChecklistItem]
	closing: list[ChecklistItem]


class PaymentMethodOut(OutputSchema):
	"""Opening/closing form: one row per MOP with Required Opening Balance (server-filtered)."""

	name: str


class PosProfileOut(OutputSchema):
	name: str
	status: str
	company: str
	opening_entry: str | None = None
	opening_entry_date: datetime | date | None = None
	checklists: list[Checklists] | None = None
	payment_methods: list[PaymentMethodOut] | None = None


class SessionListOut(OutputSchema):
	pos_profiles: list[PosProfileOut]


SessionListEnvelopeOut = SessionListOut


class CloseShiftOut(OutputSchema):
	status: str
	closing_entry: str
	is_final: bool
	entry_status: str
	error_message: str | None = None
	message: str | None = None
