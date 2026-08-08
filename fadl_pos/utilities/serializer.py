# Copyright (c) 2026, FadlTech team and contributors

from __future__ import annotations

"""Utilities serializers (passthrough until typed)."""

from fadl_pos.core.serializer import InputSchema, OutputSchema

class PassThroughIn(InputSchema):
	pass

class PassThroughOut(OutputSchema):
	pass
