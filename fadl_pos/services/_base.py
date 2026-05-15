"""Shared service base: session user gate and JSON helpers for RPC layers.

**BaseService**

* Constructor requires a logged-in user (``Guest`` → ``AuthenticationError``).
* ``_parse_json`` coerces a string body to ``dict`` / list.
* ``_cap_limit`` bounds list page sizes for GET-style queries.
"""
import frappe
from frappe import _
from frappe.utils import cint, flt

class BaseService:
    def __init__(self, user: str | None = None):
        self.user = user or frappe.session.user
        if self.user == "Guest":
            frappe.throw(_("Log in to continue."), frappe.AuthenticationError)

    def _parse_json(self, data):
        if isinstance(data, str):
            return frappe.parse_json(data)
        return data

    def _safe_int(self, val, default=0):
        try: return int(val)
        except (TypeError, ValueError): return default

    def _safe_float(self, val, default=0.0):
        try: return float(val)
        except (TypeError, ValueError): return default

    def _cap_limit(self, limit, max_val=100):
        return min(self._safe_int(limit, 20), max_val)
