import frappe
from typing import List
from fadl_pos.services.session_service import SessionService
from fadl_pos.serializers.session import BalanceDetailItem, ClosingReconciliationItem

@frappe.whitelist()
def get_list():
    """
    Check if the user has an open shift and return initialization data.
    Route: /api/method/fadl_pos.api.session.init
    """
    service = SessionService()
    return service.get_list()

@frappe.whitelist(methods=["POST"])
def open_shift(pos_profile: str, company: str, balance_details: str):
    """
    Create a new POS Opening Entry.
    Route: /api/method/fadl_pos.api.session.open_shift
    """
    parsed_balance: List[BalanceDetailItem] = frappe.parse_json(balance_details)
    
    service = SessionService()
    return service.open_shift(pos_profile, company, parsed_balance)

@frappe.whitelist(methods=["POST"])
def close_shift(opening_entry_name: str, closing_data: str = None):
    """
    Close the shift and create POS Closing Entry.
    Route: /api/method/fadl_pos.api.session.close_shift
    """
    parsed_data: List[ClosingReconciliationItem] = None
    if closing_data:
        parsed_data = frappe.parse_json(closing_data)
        
    service = SessionService()
    return service.close_shift(opening_entry_name, parsed_data)
