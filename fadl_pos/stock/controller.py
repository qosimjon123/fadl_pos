# Copyright (c) 2026, FadlTech team and contributors

"""stock controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.invoice.processing.creation import validate_cart_items as _validate_cart_items
from fadl_pos.stock.processing import availability, guards, transfer


class StockController(BaseController):
	def get_bulk_stock_availability(self, *args, **kwargs):
		return availability.get_bulk_stock_availability(*args, **kwargs)

	def get_available_qty(self, *args, **kwargs):
		return availability.get_available_qty(*args, **kwargs)

	def get_in_transit_transfers(self, *args, **kwargs):
		return transfer.get_in_transit_transfers(*args, **kwargs)

	def get_transfer_detail(self, *args, **kwargs):
		return transfer.get_transfer_detail(*args, **kwargs)

	def receive_transit_stock(self, *args, **kwargs):
		return transfer.receive_transit_stock(*args, **kwargs)

	def return_shortage_to_source(self, *args, **kwargs):
		return transfer.return_shortage_to_source(*args, **kwargs)

	def get_stock_availability(self, *args, **kwargs):
		return availability.get_pos_stock_availability(*args, **kwargs)

	def validate_cart_items(self, *args, **kwargs):
		return _validate_cart_items(*args, **kwargs)

	def validate_stock_on_invoice(self, *args, **kwargs):
		return guards.validate_stock_on_invoice(*args, **kwargs)
