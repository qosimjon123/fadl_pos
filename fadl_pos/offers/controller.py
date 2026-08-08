# Copyright (c) 2026, FadlTech team and contributors

"""offers controller — django-like actions."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.offers.processing import offers as offers_svc


class OffersController(BaseController):
	def get_offers(self, *args, **kwargs):
		return offers_svc.get_offers(*args, **kwargs)

	def get_pos_coupon(self, *args, **kwargs):
		return offers_svc.get_pos_coupon(*args, **kwargs)

	def get_active_gift_coupons(self, *args, **kwargs):
		return offers_svc.get_active_gift_coupons(*args, **kwargs)
