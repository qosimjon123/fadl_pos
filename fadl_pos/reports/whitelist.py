# Copyright (c) 2026, FadlTech team and contributors

"""reports RPC endpoints for Frappe `/api/method/...` calls."""

from __future__ import annotations

import frappe

from fadl_pos.reports.controller import ReportsController


def _controller() -> ReportsController:
	return ReportsController()


@frappe.whitelist()
def get_report_meta(*args, **kwargs):
	"""``/api/method/fadl_pos.reports.whitelist.get_report_meta``"""
	return _controller().get_report_meta(*args, **kwargs)
