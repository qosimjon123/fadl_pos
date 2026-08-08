# Copyright (c) 2026, FadlTech team and contributors

"""Normalize RPC / document dicts for stable xpos ↔ fadl_pos comparisons."""

from __future__ import annotations

from typing import Any

# Volatile Frappe metadata that must not affect parity assertions.
_STRIP_KEYS = frozenset(
	{
		"modified",
		"creation",
		"owner",
		"modified_by",
		"idx",
		"_user_tags",
		"_comments",
		"_assign",
		"_liked_by",
	}
)

_FLOAT_DP = 6


def round_float(value: float, ndigits: int = _FLOAT_DP) -> float:
	return round(float(value), ndigits)


def normalize_value(value: Any) -> Any:
	"""Recursively normalize a JSON-like value for equality checks."""
	if isinstance(value, dict):
		return normalize_rpc_dict(value)
	if isinstance(value, (list, tuple)):
		return [normalize_value(item) for item in value]
	if isinstance(value, float):
		return round_float(value)
	if isinstance(value, int) and not isinstance(value, bool):
		return value
	return value


def normalize_rpc_dict(data: dict[str, Any] | None) -> dict[str, Any]:
	"""Return a copy with volatile keys stripped, floats rounded, keys sorted.

	Sorting is applied at every dict level so ``==`` on the result is stable
	regardless of insertion order from Frappe / Pydantic dumps.
	"""
	if not data:
		return {}

	normalized: dict[str, Any] = {}
	for key in sorted(data.keys()):
		if key in _STRIP_KEYS:
			continue
		normalized[key] = normalize_value(data[key])
	return normalized


def normalize_rpc_list(rows: list[Any] | None) -> list[Any]:
	"""Normalize a list of RPC rows (or mixed scalars)."""
	return [normalize_value(row) for row in (rows or [])]


def assert_rpc_equal(left: Any, right: Any) -> None:
	"""Raise ``AssertionError`` when normalized payloads differ."""
	if normalize_value(left) != normalize_value(right):
		raise AssertionError(
			f"Normalized RPC payloads differ:\n  left={normalize_value(left)!r}\n  right={normalize_value(right)!r}"
		)
