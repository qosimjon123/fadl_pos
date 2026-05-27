"""
POS / Sales Invoice sync for fadl_pos.

Creates and updates drafts using native :class:`~erpnext.accounts.doctype.pos_invoice.pos_invoice.POSInvoice`
or :class:`~erpnext.accounts.doctype.sales_invoice.sales_invoice.SalesInvoice` controllers. Submission,
cancellation, returns, and tax/totals handling follow ERPNext: :meth:`~frappe.model.document.Document.save`
runs ``validate()`` on the controller, which applies pricing rules and
:meth:`~erpnext.controllers.accounts_controller.AccountsController.calculate_taxes_and_totals`.

Before applying client JSON we strip rolled-up amount fields so totals are never taken from the client.

**Contracts (InvoiceService)**

* ``sync(action, data)``

  - *Input*: ``action`` ∈ ``save`` | ``submit`` | ``return`` | ``void`` | ``validate``. ``data`` is a dict
    (already parsed JSON from the RPC layer).

  - *Success*:

    - ``save``: ``{\"status\": \"success\", \"name\": str, \"invoice\": dict}`` — ``invoice`` is
      ``doc.as_dict()`` after save.
    - ``submit``: ``{\"status\": \"success\", \"name\": str, \"message\": str}``.
    - ``return``: ``{\"status\": \"success\", \"name\": str, \"invoice\": dict}``.
    - ``void``: ``{\"status\": \"success\", \"name\": str, \"message\": str}``.
    - ``validate``: ``{\"valid\": bool, \"errors\": list[str], \"warnings\": list[str]}``.

  - *Errors*: Frappe exceptions (typically ``ValidationError``, ``AuthenticationError`` from ``BaseService``).
"""
from __future__ import annotations

import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from fadl_pos.serializers.invoice import InvoiceResponseSerializer


# Headers / rolled-up totals must be recomputed on the server (see AccountsController.validate).
_PARENT_TOTAL_KEYS = frozenset(
    {
        "grand_total",
        "base_grand_total",
        "rounded_total",
        "base_rounded_total",
        "rounding_adjustment",
        "base_rounding_adjustment",
        "net_total",
        "base_net_total",
        "total",
        "base_total",
        "total_taxes_and_charges",
        "base_total_taxes_and_charges",
        "discount_amount",
        "base_discount_amount",
        "outstanding_amount",
        "paid_amount",
        "base_paid_amount",
        "loyalty_amount",
        "change_amount",
        "base_change_amount",
    }
)


# Amount columns on lines are derived from qty × rate (+ tax effects) in ERPNext validators.
_ITEM_COMPUTED_KEYS = frozenset(
    {
        "amount",
        "base_amount",
        "net_amount",
        "base_net_amount",
        "taxable_value",
        "base_net_rate",
        "net_rate",
        "item_tax_amount",
        "base_tax_amount",
        "total_weight",
    }
)



def _strip_untrusted_invoice_payload(data: dict) -> dict:
    """Remove client-supplied totals so :meth:`~frappe.model.document.Document.save` recomputes them."""
    out = dict(data)
    for k in _PARENT_TOTAL_KEYS:
        out.pop(k, None)
    items = out.get("items")
    if isinstance(items, list):
        cleaned_rows = []
        for row in items:
            if isinstance(row, dict):
                r = dict(row)
                for k in _ITEM_COMPUTED_KEYS:
                    r.pop(k, None)
                cleaned_rows.append(r)
            else:
                cleaned_rows.append(row)
        out["items"] = cleaned_rows
    return out


class InvoiceService(BaseService):
    """Create/update/submit POS or Sales invoices using ERPNext document controllers."""

    def sync(self, action: str, data: dict) -> InvoiceResponseSerializer:
        """Dispatch by ``action``; see module docstring for shapes."""
        if action == "save":
            return self.save(data)
        elif action == "submit":
            return self.submit(data)
        elif action == "return":
            return self.make_return(data)
        elif action == "void":
            return self.void(data)
        elif action == "validate":
            return self.validate_cart(data)
        else:
            frappe.throw(_("Invalid action: {0}").format(action))

    @staticmethod
    def _invoice_doctype_from_settings() -> str:
        dt = frappe.db.get_single_value("POS Settings", "invoice_type") or "POS Invoice"
        return dt if dt in ("POS Invoice", "Sales Invoice") else "POS Invoice"

    @staticmethod
    def _get_existing_invoice_doc(name: str):
        if frappe.db.exists("POS Invoice", name):
            return frappe.get_doc("POS Invoice", name)
        if frappe.db.exists("Sales Invoice", name):
            return frappe.get_doc("Sales Invoice", name)
        frappe.throw(_("Invoice {0} not found").format(name))

    def save(self, data: dict) -> InvoiceResponseSerializer:
        """Create or update a draft POS/Sales invoice; doctype from POS Settings when creating."""
        sanitized = _strip_untrusted_invoice_payload(dict(data))

        name = sanitized.get("name")
        if name:
            doc = self._get_existing_invoice_doc(name)
            if doc.docstatus != 0:
                frappe.throw(_("Cannot update a submitted or cancelled invoice."))
            doc.update(sanitized)
        else:
            dt = self._invoice_doctype_from_settings()
            payload = dict(sanitized)
            payload.pop("doctype", None)
            payload["doctype"] = dt
            payload.setdefault("is_pos", 1)
            if dt == "Sales Invoice":
                payload.setdefault("is_created_using_pos", 1)
            doc = frappe.get_doc(payload)

        if hasattr(doc, "set_missing_values"):
            doc.set_missing_values()
        # Explicit parity with Desk: Selling flow recalculates in validate(); call once so callers
        # reading the document before DB commit see authoritative totals after pricing hooks.
        if hasattr(doc, "calculate_taxes_and_totals"):
            doc.calculate_taxes_and_totals()

        doc.save()

        return {
            "status": "success",
            "name": doc.name,
            "invoice": doc.as_dict(),
        }

    def submit(self, data: dict) -> InvoiceResponseSerializer:
        """Save then submit via :meth:`~frappe.model.document.Document.submit`."""
        save_res = self.save(data)
        name = save_res["name"]
        inv = save_res.get("invoice") or {}
        dt = inv.get("doctype")
        if dt not in ("POS Invoice", "Sales Invoice"):
            dt = self._get_existing_invoice_doc(name).doctype

        doc = frappe.get_doc(dt, name)
        doc.submit()

        return {
            "status": "success",
            "name": doc.name,
            "message": _("Invoice {0} submitted successfully").format(doc.name),
        }

    def make_return(self, data: dict) -> InvoiceResponseSerializer:
        """
        Desk-equivalent return: empty invoice shell + native ``make_sales_return`` with ``target_doc``,
        then profile/warehouse + ``set_missing_values`` / ``calculate_taxes_and_totals``.

        Mirrors ``pos_controller.js`` (``make_invoice_frm`` → ``make_return_invoice`` →
        ``set_pos_profile_data`` / ``set_pos_data``).
        """
        from erpnext.accounts.doctype.pos_invoice.pos_invoice import (
            make_sales_return as make_pos_invoice_return,
        )
        from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
            make_sales_return as make_sales_invoice_return,
        )

        source_name = data.get("return_against")
        if not source_name:
            frappe.throw(_("Original invoice name is required for return."))

        if frappe.db.exists("POS Invoice", source_name):
            inv_doctype = "POS Invoice"
            source_doc = frappe.get_doc("POS Invoice", source_name)
            make_return_fn = make_pos_invoice_return
        elif frappe.db.exists("Sales Invoice", source_name):
            inv_doctype = "Sales Invoice"
            source_doc = frappe.get_doc("Sales Invoice", source_name)
            make_return_fn = make_sales_invoice_return
        else:
            frappe.throw(_("Invoice {0} not found").format(source_name))

        if source_doc.docstatus != 1:
            frappe.throw(_("You can only return against a submitted invoice."))

        from erpnext.controllers.sales_and_purchase_return import is_invoice_returnable
        if not is_invoice_returnable(inv_doctype, source_name):
            frappe.throw(_("All the items have been already returned."))

        # Desk: make_invoice_frm — new blank doc with POS flags before mapping return onto it.
        target_doc = frappe.new_doc(inv_doctype)
        target_doc.set("items", [])
        target_doc.is_pos = 1
        if inv_doctype == "Sales Invoice":
            target_doc.is_created_using_pos = 1

        return_doc = make_return_fn(source_name, target_doc)

        # Desk: set_pos_profile_data — session profile / warehouse (optional RPC overrides).
        company = data.get("company") or return_doc.company or source_doc.company
        pos_profile = (
            data.get("pos_profile")
            or return_doc.get("pos_profile")
            or source_doc.get("pos_profile")
        )
        return_doc.company = company
        if pos_profile:
            return_doc.pos_profile = pos_profile

        set_wh = data.get("set_warehouse")
        if set_wh:
            return_doc.set_warehouse = set_wh
        elif pos_profile:
            profile_wh = frappe.db.get_value("POS Profile", pos_profile, "warehouse")
            if profile_wh:
                return_doc.set_warehouse = profile_wh

        if hasattr(return_doc, "set_missing_values"):
            return_doc.set_missing_values()
        if hasattr(return_doc, "calculate_taxes_and_totals"):
            return_doc.calculate_taxes_and_totals()

        return_doc.insert()

        return {
            "status": "success",
            "name": return_doc.name,
            "invoice": return_doc.as_dict(),
        }

    def void(self, data: dict) -> InvoiceResponseSerializer:
        """Cancel submitted invoice or delete draft."""
        name = data.get("name")
        if not name:
            frappe.throw(_("Invoice name is required."))

        doc = self._get_existing_invoice_doc(name)

        if doc.docstatus == 1:
            doc.cancel()
        elif doc.docstatus == 0:
            frappe.delete_doc(doc.doctype, name)

        return {
            "status": "success",
            "name": name,
            "message": _("Invoice {0} voided").format(name),
        }

    def validate_cart(self, data: dict):
        """Pre-flight stock (and optional price list) checks; does not persist."""
        from fadl_pos.services.validation_service import ValidationService

        return ValidationService.validate_cart_items(
            data.get("items", []),
            data.get("warehouse")
        )
