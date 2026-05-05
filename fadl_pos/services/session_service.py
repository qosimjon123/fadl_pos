import frappe
from frappe import _

from fadl_pos.services._base import BaseService
from erpnext.selling.page.point_of_sale.point_of_sale import (
    check_opening_entry,
    create_opening_voucher,
    get_pos_profile_data
)
from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening

class SessionService(BaseService):
    def get_init_data(self):
        """
        Check if there is an open shift for the user,
        and fetch POS profile data if an open shift exists.
        """
        open_vouchers = check_opening_entry(self.user)
        
        data = {
            "has_open_shift": False,
            "opening_entry": None,
            "pos_profile": None,
            "company": None
        }

        if open_vouchers:
            opening_entry = open_vouchers[0]
            data["has_open_shift"] = True
            data["opening_entry"] = opening_entry
            
            # Fetch profile details for the active session
            profile_data = get_pos_profile_data(opening_entry.pos_profile)
            data["pos_profile_data"] = profile_data
            data["pos_profile"] = opening_entry.pos_profile
            data["company"] = opening_entry.company
            
        return data

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
