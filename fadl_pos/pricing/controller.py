# Copyright (c) 2026, FadlTech team and contributors

"""pricing controller — django-like actions."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.pricing.processing import rules as pricing_rules


class PricingController(BaseController):
	def get_active_pricing_rules(self, *args, **kwargs):
		return pricing_rules.get_active_pricing_rules(*args, **kwargs)

	def reconcile_line_prices(self, *args, **kwargs):
		return pricing_rules.reconcile_line_prices(*args, **kwargs)
