from erpnext.accounts.doctype.payment_request.test_payment_request import payment_method
from typing import TypedDict, List
import frappe
from frappe import _

from fadl_pos.services._base import BaseService

from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening

from fadl_pos.serializers.session import (
    SessionListResponseSerializer,
    ClosingReconciliationItem,
    CloseShiftResponse,
    BalanceDetailItem
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

    def _create_opening_voucher(self, pos_profile, company, balance_details):
        """
        rewrited native create_opening_voucher from point-of-sale.py
        """
        new_pos_opening = frappe.get_doc(
            {
                "doctype": "POS Opening Entry",
                "period_start_date": frappe.utils.get_datetime(),
                "posting_date": frappe.utils.getdate(),
                "user": frappe.session.user,
                "pos_profile": pos_profile,
                "company": company,
            }
        )
        new_pos_opening.set("balance_details", balance_details)
        new_pos_opening.submit()

        return new_pos_opening.as_dict()
        
    def _check_opening_entry(self, user=None, pos_profile=None):
        """
        Check for open POS Opening Entries by user and/or POS Profile.
        """
        filters = {"pos_closing_entry": ["in", ["", None]], "docstatus": 1}
        if user:
            filters["user"] = user
        if pos_profile:
            filters["pos_profile"] = pos_profile

        return frappe.db.get_all(
            "POS Opening Entry",
            filters=filters,
            fields=["name", "company", "pos_profile", "user", "period_start_date"],
            order_by="period_start_date desc"
        )

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
            status = "Close"
            if active_entry and active_entry.pos_profile == profile_name:
                opening_entry_name = active_entry.name
                status = "Open"

            profile_dict = {
                "name": profile_name,
                "status": status,
                "company": company,
                "opening_entry": opening_entry_name,
            }

            # If the shift is closed, we need to gather opening requirements
            if status == "Close":
                # Fetch payment methods for this profile
                payment_docs = self._get_profile_payment_methods(profile_name)
                
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






    def open_shift(self, pos_profile: str, company: str, balance_details: List[BalanceDetailItem]) -> List[SessionListResponseSerializer]:
        """
        Create a new POS Opening Entry (open shift).
        balance_details: list of dicts with 'mode_of_payment' and 'opening_amount'
        """
        # 1. Prevent duplicate shifts for the same user
        if self._check_opening_entry(user=self.user):
            frappe.throw(_("You already have an open POS shift. Please close it before opening a new one."))

        # 2. Prevent multiple users from opening the same POS Profile
        if self._check_opening_entry(pos_profile=pos_profile):
            frappe.throw(_("POS Profile {0} is already in use by another cashier.").format(frappe.bold(pos_profile)))

        self._create_opening_voucher(pos_profile, company, balance_details)
        
        # Return the simplified active profile list, ensuring consistency
        return self.get_list()

    def close_shift(self, opening_entry_name: str, closing_data: List[ClosingReconciliationItem] = None) -> CloseShiftResponse:
        """
        Create and submit a POS Closing Entry from an opening entry.
        """
        opening_entry = frappe.get_doc("POS Opening Entry", opening_entry_name)
            
        if opening_entry.status != "Open":
            frappe.throw(_("This POS Opening Entry is already closed or cancelled."))

        if opening_entry.user != self.user:
            frappe.throw(_("You can only close your own shift."))

        # 1. Generate closing entry from native builder
        closing_entry = make_closing_entry_from_opening(opening_entry)
        
        # Ensure date/time are set (Native validate behavior can be inconsistent depending on server time)
        closing_entry.posting_date = frappe.utils.nowdate()
        closing_entry.posting_time = frappe.utils.nowtime()

        # 2. Merge and Fix Reconciliation logic
        # We need to map opening amounts and user input actual amounts
        opening_amounts = {d.mode_of_payment: frappe.utils.flt(d.opening_amount) for d in opening_entry.balance_details}
        actual_map = {p.get("mode_of_payment"): frappe.utils.flt(p.get("closing_amount", 0)) for p in (closing_data or [])}
        
        existing_mops = []
        for row in closing_entry.payment_reconciliation:
            existing_mops.append(row.mode_of_payment)
            
            # Transfer Opening Amount
            opening_amt = opening_amounts.get(row.mode_of_payment, 0)
            row.opening_amount = opening_amt
            
            # CRITICAL FIX: expected_amount = opening + sales
            # Native builder 'make_closing_entry_from_opening' only sets row.expected_amount = sales_amount
            row.expected_amount += opening_amt
            
            # Default closing_amount to expected_amount (Desk behavior: assume no discrepancy if not specified)
            row.closing_amount = row.expected_amount
            
            # Apply user override if exists
            if row.mode_of_payment in actual_map:
                row.closing_amount = actual_map[row.mode_of_payment]
            
            # Calculate difference (Calculated in JS in native Desk)
            row.difference = frappe.utils.flt(row.closing_amount) - frappe.utils.flt(row.expected_amount)
                
        # Append payment methods that were in the opening entry but had NO transactions
        for mop, opening_amt in opening_amounts.items():
            if mop not in existing_mops:
                closing_entry.append("payment_reconciliation", {
                    "mode_of_payment": mop,
                    "opening_amount": opening_amt,
                    "expected_amount": opening_amt,
                    "closing_amount": actual_map.get(mop, opening_amt), # Default to opening if no sales and no input
                    "difference": actual_map.get(mop, opening_amt) - opening_amt
                })
        
        # 3. Save and submit
        closing_entry.insert(ignore_permissions=True)
        closing_entry.submit()
        
        # Reload to capture status change (e.g., to 'Queued' if consolidation is backgrounded)
        closing_entry.load_from_db()
        
        return {
            "status": "success" if closing_entry.status in ["Submitted", "Queued"] else "failed",
            "closing_entry": closing_entry.name,
            "entry_status": closing_entry.status,
            "error_message": closing_entry.error_message if closing_entry.status == "Failed" else None
        }
