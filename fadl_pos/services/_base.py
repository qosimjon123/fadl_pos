"""Shared service base: session user gate for RPC layers."""

import frappe
from frappe import _


class BaseService:
	def __init__(self, user: str | None = None):
		self.user = user or frappe.session.user
		if self.user == "Guest":
			frappe.throw(_("Log in to continue."), frappe.AuthenticationError)
