from erpnext.accounts.doctype.payment_request.test_payment_request import payment_method
from typing import TypedDict, List
import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from erpnext.selling.page.point_of_sale.point_of_sale import (
    check_opening_entry,
    create_opening_voucher,
    get_pos_profile_data
)
from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening

from fadl_pos.serializers.session import (
    PosProfileNative,
    SessionListResponseSerializer,
    PosProfileResponseSerializer,
    PaymentMethodSerializer
)

class SessionService(BaseService):

    def _get_profiles(self, user):
        """
        rewrited native pos_profile_query from pos_profile.py
        Returns list of dicts with name and company.
        """
        return frappe.db.sql(
            """
            SELECT pf.name, pf.company
            FROM `tabPOS Profile` pf
            INNER JOIN `tabPOS Profile User` pfu ON pfu.parent = pf.name
            WHERE pfu.user = %(user)s AND pf.disabled = 0
            """,
            {"user": user},
            as_dict=True
        )

    def _check_opening_entry(self, user):
        """
        rewrited native check_opening_entry from point-of-sale.py
        """
        open_vouchers = frappe.db.get_all(
            "POS Opening Entry",
            filters={"user": user, "pos_closing_entry": ["in", ["", None]], "docstatus": 1},
            fields=["name", "company", "pos_profile", "period_start_date"],
            order_by="period_start_date desc",
            limit=1
        )
        return open_vouchers

    def get_list(self) -> List[SessionListResponseSerializer]:
        """
        Check if there is an open shift for the user,
        and fetch POS profile data if an open shift exists.
        """
        profiles = self._get_profiles(self.user)
        open_vouchers = self._check_opening_entry(self.user)
        active_entry = open_vouchers[0] if open_vouchers else None

        pos_profiles_response = []

        for profile in profiles:
            profile_name = profile.get("name")
            company = profile.get("company")
            
            # Determine session status
            opening_entry_name = None
            status = "Inactive"
            if active_entry and active_entry.pos_profile == profile_name:
                opening_entry_name = active_entry.name
                status = "Active"

            profile_dict = {
                "name": profile_name,
                "status": status,
                "company": company,
                "opening_entry": opening_entry_name,
            }

            # If the shift is inactive, we need to gather opening requirements
            if status == "Inactive":
                # Fetch payment methods for this profile
                payment_docs = frappe.db.get_all(
                    "POS Payment Method",
                    filters={"parent": profile_name, "parenttype": "POS Profile"},
                    fields=["mode_of_payment", "default"]
                )
                
                payment_methods = []
                for pm in payment_docs:
                    mop_type = frappe.db.get_value("Mode of Payment", pm.mode_of_payment, "type")
                    payment_methods.append({
                        "name": pm.mode_of_payment,
                        "default": pm.default,
                        "type": mop_type,
                        "required_ob": bool(mop_type == "Cash")
                    })

                profile_dict["checklists"] = [
                    {"opening": []},
                    {"closing": []}
                ]
                profile_dict["payment_methods"] = payment_methods

            pos_profiles_response.append(profile_dict)

        return [{
            "pos_profiles": pos_profiles_response
        }]






    def open_shift(self, pos_profile: str, company: str, balance_details: str | list | dict):
        """
        Create a new POS Opening Entry (open shift).
        balance_details: list of dicts with 'mode_of_payment' and 'opening_amount'
        """
        if not pos_profile or not company:
            frappe.throw(_("POS Profile and Company are required to open a shift."))
            
        if isinstance(balance_details, (list, dict)):
            balance_details = frappe.as_json(balance_details)

        # check_opening_entry verifies if user already has an open shift
        open_vouchers = check_opening_entry(self.user)
        if open_vouchers:
            frappe.throw(_("You already have an open shift: {0}").format(open_vouchers[0].name))

        new_entry = create_opening_voucher(pos_profile, company, balance_details)
        return new_entry

    def close_shift(self, opening_entry_name: str, closing_data: dict = None):
        """
        Create and submit a POS Closing Entry from an opening entry.
        """
        opening_entry = frappe.get_doc("POS Opening Entry", opening_entry_name)
        if opening_entry.status != "Open":
            frappe.throw(_("Opening Entry {0} is already closed.").format(opening_entry_name))
            
        if opening_entry.user != self.user:
            frappe.throw(_("You can only close your own shift."))

        # 1. Generate closing entry from native builder
        closing_entry = make_closing_entry_from_opening(opening_entry)
        
        # 2. Update actual balances based on user input (closing_data)
        if closing_data and closing_data.get("payment_reconciliation"):
            # Update expected amounts
            actual_payments = closing_data.get("payment_reconciliation")
            # Map by mode_of_payment
            actual_map = {p.get("mode_of_payment"): flt(p.get("closing_amount", 0)) for p in actual_payments}
            
            for row in closing_entry.payment_reconciliation:
                if row.mode_of_payment in actual_map:
                    row.closing_amount = actual_map[row.mode_of_payment]
                    
        # 3. Save and submit
        closing_entry.insert(ignore_permissions=True)
        closing_entry.submit()
        
        return closing_entry.as_dict()
