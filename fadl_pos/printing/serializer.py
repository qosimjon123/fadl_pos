# Copyright (c) 2026, FadlTech team and contributors

"""Pydantic schemas for printing RPC (permissive pass-through during port)."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from fadl_pos.core.serializer import InputSchema, OutputSchema


class PassThroughIn(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class PassThroughOut(OutputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)
