# Copyright (c) 2026, FadlTech team and contributors
"""Normalize whitelisted RPC parameters (HTTP form/JSON can send non-string types)."""

from __future__ import annotations

# Frappe passes the full ``form_dict`` into whitelisted methods, including ``cmd``.
RPC_NOISE_KEYS = frozenset({"cmd"})


def strip_rpc_noise(kwargs: dict) -> dict:
	"""Drop keys that are not domain parameters."""
	return {k: v for k, v in kwargs.items() if k not in RPC_NOISE_KEYS}
