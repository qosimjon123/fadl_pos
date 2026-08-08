# Copyright (c) 2026, FadlTech team and contributors

"""Smoke-import all ported feature modules."""

from __future__ import annotations

import importlib
import unittest


MODULES = (
	"fadl_pos.catalog.whitelist",
	"fadl_pos.stock.whitelist",
	"fadl_pos.stock.processing.guards",
	"fadl_pos.offers.whitelist",
	"fadl_pos.delivery.whitelist",
	"fadl_pos.invoice.whitelist",
	"fadl_pos.invoice.events",
	"fadl_pos.invoice.overrides.pos_invoice",
	"fadl_pos.invoice.overrides.pos_invoice_merge_log",
	"fadl_pos.payment.whitelist",
	"fadl_pos.cash.whitelist",
	"fadl_pos.permissions.whitelist",
	"fadl_pos.printing.whitelist",
	"fadl_pos.printing.jinja_helpers",
	"fadl_pos.purchasing.whitelist",
	"fadl_pos.sync.whitelist",
	"fadl_pos.integrations.processing.fbr",
	"fadl_pos.integrations.controller",
	"fadl_pos.barcode.whitelist",
	"fadl_pos.settings.boot",
	"fadl_pos.settings.controller",
	"fadl_pos.sales_orders.whitelist",
	"fadl_pos.pricing.whitelist",
	"fadl_pos.taxes.whitelist",
	"fadl_pos.reports.whitelist",
	"fadl_pos.utilities.whitelist",
	"fadl_pos.utilities.controller",
	"fadl_pos.utilities.processing.helpers",
	"fadl_pos.cash.processing.posting",
	"fadl_pos.purchasing.processing.orders",
	"fadl_pos.payment.processing.credit",
	"fadl_pos.offers.processing.offers",
	"fadl_pos.delivery.processing.charges",
)


class TestImportSmoke(unittest.TestCase):
	def test_all_ported_modules_import(self):
		errors: list[str] = []
		for name in MODULES:
			try:
				importlib.import_module(name)
			except Exception as exc:  # noqa: BLE001 - collect all failures
				errors.append(f"{name}: {type(exc).__name__}: {exc}")
		self.assertEqual(errors, [], msg="\n".join(errors))
