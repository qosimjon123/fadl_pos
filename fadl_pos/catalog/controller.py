# Copyright (c) 2026, FadlTech team and contributors

"""catalog controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.catalog.processing import bundles, items, price, price_check


class CatalogController(BaseController):
	def get_pos_items(self, *args, **kwargs):
		return items.get_pos_items(*args, **kwargs)

	def get_items_count(self, *args, **kwargs):
		return items.get_items_count(*args, **kwargs)

	def get_item_groups(self, *args, **kwargs):
		return items.get_item_groups(*args, **kwargs)

	def search_barcode(self, *args, **kwargs):
		return items.search_barcode(*args, **kwargs)

	def get_item_detail(self, *args, **kwargs):
		return items.get_item_detail(*args, **kwargs)

	def get_item_variants(self, *args, **kwargs):
		return items.get_item_variants(*args, **kwargs)

	def get_item_attributes(self, *args, **kwargs):
		return items.get_item_attributes(*args, **kwargs)

	def update_price_list_rate(self, *args, **kwargs):
		return price.update_price_list_rate(*args, **kwargs)

	def get_price_for_uom(self, *args, **kwargs):
		return price.get_price_for_uom(*args, **kwargs)

	def get_bundle_components(self, *args, **kwargs):
		return bundles.get_bundle_components(*args, **kwargs)

	def lookup(self, *args, **kwargs):
		return price_check.lookup(*args, **kwargs)

	def get_terminal_context(self, *args, **kwargs):
		return price_check.get_terminal_context(*args, **kwargs)
