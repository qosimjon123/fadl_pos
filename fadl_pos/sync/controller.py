# Copyright (c) 2026, FadlTech team and contributors

"""sync controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController

from fadl_pos.sync.processing.sync import get_child_table_data as _get_child_table_data
from fadl_pos.sync.processing.sync import get_item_prices as _get_item_prices

class SyncController(BaseController):
	def get_child_table_data(self, *args, **kwargs):
		return _get_child_table_data(*args, **kwargs)

	def get_item_prices(self, *args, **kwargs):
		return _get_item_prices(*args, **kwargs)
