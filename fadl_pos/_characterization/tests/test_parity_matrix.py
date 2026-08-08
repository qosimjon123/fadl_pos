# Copyright (c) 2026, FadlTech team and contributors

"""xpos → fadl_pos RPC parity matrix (data + placeholder comparison test).

Lists the ~17 key RPC mappings for catalog / stock / offers / invoice / payment.
Live side-by-side comparison is skipped until both sides are importable.
"""

from __future__ import annotations

import importlib
import unittest
from typing import Any

from fadl_pos._characterization.normalize import assert_rpc_equal, normalize_value

# (id, domain, xpos_method, fadl_pos_method, notes)
RPC_PARITY_MATRIX: list[dict[str, str]] = [
	{
		"id": "1",
		"domain": "catalog",
		"xpos": "xpos.api.items.get_pos_items",
		"fadl_pos": "fadl_pos.catalog.whitelist.get_pos_items",
		"notes": "item browse / search / pagination",
	},
	{
		"id": "2",
		"domain": "catalog",
		"xpos": "xpos.api.items.get_item_groups",
		"fadl_pos": "fadl_pos.catalog.whitelist.get_item_groups",
		"notes": "item group tree for POS profile",
	},
	{
		"id": "3",
		"domain": "catalog",
		"xpos": "xpos.api.items.search_barcode",
		"fadl_pos": "fadl_pos.catalog.whitelist.search_barcode",
		"notes": "barcode → item (scale branch optional)",
	},
	{
		"id": "4",
		"domain": "catalog",
		"xpos": "xpos.api.items.get_item_detail",
		"fadl_pos": "fadl_pos.catalog.whitelist.get_item_detail",
		"notes": "detail incl. batches / UOMs / rate",
	},
	{
		"id": "5",
		"domain": "stock",
		"xpos": "xpos.api.items.get_stock_availability",
		"fadl_pos": "fadl_pos.stock.whitelist.get_stock_availability",
		"notes": "bulk availability; pending POS qty deducted",
	},
	{
		"id": "6",
		"domain": "stock",
		"xpos": "xpos.x_pos.api.invoice_processing.creation.validate_cart_items",
		"fadl_pos": "fadl_pos.stock.whitelist.validate_cart_items",
		"notes": "cart-level guard; may be controller-only",
	},
	{
		"id": "7",
		"domain": "offers",
		"xpos": "xpos.api.offers.get_offers",
		"fadl_pos": "fadl_pos.offers.whitelist.get_offers",
		"notes": "active POS Offer rows for profile",
	},
	{
		"id": "8",
		"domain": "offers",
		"xpos": "xpos.api.offers.get_pos_coupon",
		"fadl_pos": "fadl_pos.offers.whitelist.get_pos_coupon",
		"notes": "coupon validity / customer / max use",
	},
	{
		"id": "9",
		"domain": "offers",
		"xpos": "xpos.api.offers.get_applicable_delivery_charges",
		"fadl_pos": "fadl_pos.delivery.whitelist.get_applicable_delivery_charges",
		"notes": "delivery module; skip if delivery out of scope",
	},
	{
		"id": "10",
		"domain": "invoice",
		"xpos": "xpos.api.invoices.create_invoice",
		"fadl_pos": "fadl_pos.invoice.whitelist.create_invoice",
		"notes": "cash, single item happy path",
	},
	{
		"id": "11",
		"domain": "invoice",
		"xpos": "xpos.api.invoices.create_invoice",
		"fadl_pos": "fadl_pos.invoice.whitelist.create_invoice",
		"notes": "split payment tender",
	},
	{
		"id": "12",
		"domain": "invoice",
		"xpos": "xpos.api.invoices.create_invoice",
		"fadl_pos": "fadl_pos.invoice.whitelist.create_invoice",
		"notes": "return against original invoice",
	},
	{
		"id": "13",
		"domain": "invoice",
		"xpos": "xpos.api.invoices.save_draft_invoice",
		"fadl_pos": "fadl_pos.invoice.whitelist.save_draft_invoice",
		"notes": "paired with get_draft_invoices",
	},
	{
		"id": "14",
		"domain": "invoice",
		"xpos": "xpos.api.invoices.get_invoice_details",
		"fadl_pos": "fadl_pos.invoice.whitelist.get_invoice_details",
		"notes": "full invoice payload for receipt / return",
	},
	{
		"id": "15",
		"domain": "payment",
		"xpos": "xpos.api.payments.get_outstanding_invoices",
		"fadl_pos": "fadl_pos.payment.whitelist.get_outstanding_invoices",
		"notes": "customer outstanding list",
	},
	{
		"id": "16",
		"domain": "payment",
		"xpos": "xpos.api.payments.create_payment_entry",
		"fadl_pos": "fadl_pos.payment.whitelist.create_payment_entry",
		"notes": "manual Payment Entry against SI",
	},
	{
		"id": "17",
		"domain": "payment",
		"xpos": "xpos.x_pos.api.payment_processing.processor.process_pos_payment",
		"fadl_pos": "fadl_pos.payment.whitelist.process_pos_payment",
		"notes": "post-submit payment processor entrypoint",
	},
]


def _callable_exists(dotted: str) -> bool:
	if "." not in dotted:
		return False
	module_path, _, attr = dotted.rpartition(".")
	try:
		module = importlib.import_module(module_path)
	except ImportError:
		return False
	return callable(getattr(module, attr, None))


def _resolve_callable(dotted: str):
	module_path, _, attr = dotted.rpartition(".")
	module = importlib.import_module(module_path)
	return getattr(module, attr)


class TestParityMatrixDocumented(unittest.TestCase):
	"""Structural checks on the mapping table itself (no RPC calls)."""

	def test_matrix_has_seventeen_entries(self):
		self.assertEqual(len(RPC_PARITY_MATRIX), 17)

	def test_domains_cover_catalog_stock_offers_invoice_payment(self):
		domains = {row["domain"] for row in RPC_PARITY_MATRIX}
		self.assertEqual(domains, {"catalog", "stock", "offers", "invoice", "payment"})

	def test_ids_are_unique_and_sequential(self):
		ids = [row["id"] for row in RPC_PARITY_MATRIX]
		self.assertEqual(ids, [str(i) for i in range(1, 18)])

	def test_every_row_has_both_paths(self):
		for row in RPC_PARITY_MATRIX:
			self.assertTrue(row["xpos"].startswith("xpos."), row)
			self.assertTrue(row["fadl_pos"].startswith("fadl_pos."), row)


class TestXposFadlPosParity(unittest.TestCase):
	"""Placeholder: compare normalized xpos vs fadl_pos RPC results.

	Enable per-row once both callables import. Side-effect assertions (SLE / GL /
	coupon ``used`` / PE) belong in later IntegrationTestCase cases that reuse
	:mod:`fadl_pos._characterization.fixtures`.
	"""

	def _ready_rows(self) -> list[dict[str, str]]:
		ready = []
		for row in RPC_PARITY_MATRIX:
			if _callable_exists(row["xpos"]) and _callable_exists(row["fadl_pos"]):
				ready.append(row)
		return ready

	def test_parity_matrix_comparison_placeholder(self):
		ready = self._ready_rows()
		if not ready:
			self.skipTest(
				"No RPC pair is importable on both xpos and fadl_pos yet; "
				"matrix is documented in RPC_PARITY_MATRIX."
			)

		# When modules exist, callers should supply args via a fixture harness.
		# This placeholder only proves both sides resolve and normalize cleanly.
		failures: list[str] = []
		for row in ready:
			try:
				xpos_fn = _resolve_callable(row["xpos"])
				fadl_fn = _resolve_callable(row["fadl_pos"])
			except Exception as exc:  # pragma: no cover
				failures.append(f"{row['id']}: resolve failed: {exc}")
				continue
			# Without a shared args harness we only confirm callables exist.
			_ = (xpos_fn, fadl_fn, normalize_value)
			# Intentionally not invoking RPCs here — needs site fixtures + args.
		if failures:
			self.fail("; ".join(failures))
		self.skipTest(
			f"{len(ready)} RPC pair(s) importable; invoke with shared args + "
			"assert_rpc_equal once characterization fixtures are materialized."
		)

	def test_assert_rpc_equal_helper_roundtrip(self):
		"""Sanity: normalize helpers used by future parity cases."""
		sample: dict[str, Any] = {
			"name": "INV-1",
			"grand_total": 10.123456789,
			"creation": "2026-01-01 00:00:00",
			"owner": "Administrator",
			"items": [{"qty": 1, "rate": 10.0}],
		}
		clone = {
			"items": [{"rate": 10.0, "qty": 1}],
			"grand_total": 10.123457,
			"name": "INV-1",
			"modified": "2026-08-01 12:00:00",
			"owner": "Other",
			"creation": "ignored",
		}
		assert_rpc_equal(sample, clone)


if __name__ == "__main__":
	unittest.main()
