# Copyright (c) 2026, FadlTech team and contributors

from __future__ import annotations

from pydantic import ConfigDict

from fadl_pos.core.serializer import InputSchema, OutputSchema


class PassThroughIn(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class PassThroughOut(OutputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)
