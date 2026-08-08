# Copyright (c) 2026, FadlTech team and contributors

"""Delivery charges controller."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.delivery.processing import charges as charges_svc


class DeliveryController(BaseController):
	def get_delivery_charges(self, *args, **kwargs):
		return charges_svc.get_delivery_charges(*args, **kwargs)

	def get_applicable_delivery_charges(self, *args, **kwargs):
		return charges_svc.get_applicable_delivery_charges(*args, **kwargs)
