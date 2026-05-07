import frappe
from frappe import _
from typing import List
from fadl_pos.services.session_service import SessionService
from fadl_pos.serializers.session import BalanceDetailItem, ClosingReconciliationItem

@frappe.whitelist()
def get_list():
    """
    Check if the user has an open shift and return initialization data.
    Route: /api/method/fadl_pos.api.session.get_list
    """
    return SessionService().get_list()

@frappe.whitelist(methods=["POST"])
def open_shift(pos_profile: str, company: str, balance_details: str):
    """
    Create a new POS Opening Entry.
    Route: /api/method/fadl_pos.api.session.open_shift
    """
    if not pos_profile or not company:
        frappe.throw(_("POS Profile and Company are required to open a shift."))
    
    service = SessionService()
    parsed_balance: List[BalanceDetailItem] = service._parse_json(balance_details)
    return service.open_shift(pos_profile, company, parsed_balance)

@frappe.whitelist(methods=["POST"])
def close_shift(opening_entry_name: str, closing_data: str = None):
    """
    Close the shift and create POS Closing Entry.
    Route: /api/method/fadl_pos.api.session.close_shift
    """
    if not opening_entry_name:
        frappe.throw(_("Opening Entry Name is required to close the shift."))
    
    service = SessionService()
    parsed_data: List[ClosingReconciliationItem] = service._parse_json(closing_data) if closing_data else None
    return service.close_shift(opening_entry_name, parsed_data)
