# Copyright (c) 2026, FadlTech team and contributors

"""Frappe RPC boundary: validate In models, normalize Out."""

from __future__ import annotations

from typing import Any, TypeVar

import frappe
from pydantic import BaseModel, ValidationError

from fadl_pos.schemas import InputSchema, OutputSchema

TIn = TypeVar("TIn", bound=InputSchema)
TOut = TypeVar("TOut", bound=OutputSchema)


def raise_validation_error(exc: ValidationError) -> None:
	frappe.throw(str(exc.errors()), frappe.ValidationError)


def validate_in(model: type[TIn], raw: dict[str, Any] | None) -> TIn:
	try:
		return model.model_validate(raw or {})
	except ValidationError as exc:
		raise_validation_error(exc)
		raise AssertionError("unreachable")


def dump_out(model: type[TOut], result: Any) -> dict[str, Any]:
	"""Serialize service result through Out schema (idempotent if already shaped)."""
	if isinstance(result, dict):
		return model.dump(result)
	return result


def dump_out_list(model: type[TOut], results: list[Any]) -> list[dict[str, Any]]:
	return [dump_out(model, item) for item in results]
