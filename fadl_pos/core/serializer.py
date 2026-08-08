# Copyright (c) 2026, FadlTech team and contributors

"""Shared Pydantic v2 base schemas and the Frappe RPC boundary (validate in / dump out).

Every feature module's ``serializer.py`` should build its In/Out models on top of
:class:`InputSchema` / :class:`OutputSchema`, and its ``whitelist.py`` should call
:func:`validate_in` / :func:`dump_out` at the RPC boundary.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from fadl_pos.core.errors import validation_error


class InputSchema(BaseModel):
	model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OutputSchema(BaseModel):
	model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

	@classmethod
	def dump(cls, data: Any) -> dict[str, Any]:
		return cls.model_validate(data).model_dump()


TIn = TypeVar("TIn", bound=InputSchema)
TOut = TypeVar("TOut", bound=OutputSchema)


def validate_in(model: type[TIn], raw: dict[str, Any] | None) -> TIn:
	try:
		return model.model_validate(raw or {})
	except ValidationError as exc:
		validation_error(exc)
		raise AssertionError("unreachable")


def dump_out(model: type[TOut], result: Any) -> dict[str, Any]:
	"""Serialize service result through Out schema (idempotent if already shaped)."""
	if isinstance(result, dict):
		return model.dump(result)
	return result


def dump_out_list(model: type[TOut], results: list[Any]) -> list[dict[str, Any]]:
	return [dump_out(model, item) for item in results]
