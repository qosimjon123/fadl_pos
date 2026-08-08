# Copyright (c) 2026, FadlTech team and contributors

"""taxes controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController

from fadl_pos.taxes.processing.taxes import get_item_tax_template as _get_item_tax_template
from fadl_pos.taxes.processing.taxes import get_item_tax_templates_bulk as _get_item_tax_templates_bulk

class TaxesController(BaseController):
	def get_item_tax_template(self, *args, **kwargs):
		return _get_item_tax_template(*args, **kwargs)

	def get_item_tax_templates_bulk(self, *args, **kwargs):
		return _get_item_tax_templates_bulk(*args, **kwargs)
