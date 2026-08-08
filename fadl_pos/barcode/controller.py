# Copyright (c) 2026, FadlTech team and contributors

"""barcode controller — django-like actions."""

from __future__ import annotations

from fadl_pos.barcode.processing import service as barcode_svc
from fadl_pos.core.permission import BaseController


class BarcodeController(BaseController):
	def get_barcode_image(self, *args, **kwargs):
		return barcode_svc.get_barcode_image(*args, **kwargs)

	def get_qrcode_image(self, *args, **kwargs):
		return barcode_svc.get_qrcode_image(*args, **kwargs)

	def get_item_barcode_labels(self, *args, **kwargs):
		return barcode_svc.get_item_barcode_labels(*args, **kwargs)

	def get_barcode_types(self, *args, **kwargs):
		return barcode_svc.get_barcode_types(*args, **kwargs)

	def search_items_for_barcode(self, *args, **kwargs):
		return barcode_svc.search_items_for_barcode(*args, **kwargs)
