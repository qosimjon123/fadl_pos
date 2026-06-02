"""Shared service base: session user gate for RPC layers."""

from typing import Any

import frappe
from frappe import _

from fadl_pos.schemas import OutputSchema


class BaseService:
	def __init__(self, user: str | None = None):
		self.user = user or frappe.session.user
		if self.user == "Guest":
			frappe.throw(_("Log in to continue."), frappe.AuthenticationError)

	@staticmethod
	def dump_out(model: type[OutputSchema], data: Any) -> dict[str, Any]:
		return model.dump(data)
