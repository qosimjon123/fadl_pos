import frappe
from fadl_pos.services.session_service import SessionService

@frappe.whitelist()
def init():
    """
    Check if the user has an open shift and return initialization data.
    Route: /api/method/fadl_pos.api.session.init
    """
    service = SessionService()
    return service.get_init_data()

@frappe.whitelist()
def open_shift(pos_profile: str, company: str, balance_details: str):
    """
    Create a new POS Opening Entry.
    Route: /api/method/fadl_pos.api.session.open_shift
    """
    service = SessionService()
    return service.open_shift(pos_profile, company, balance_details)

@frappe.whitelist()
def close_shift(opening_entry_name: str, closing_data: str = None):
    """
    Close the shift and create POS Closing Entry.
    Route: /api/method/fadl_pos.api.session.close_shift
    """
    service = SessionService()
    parsed_data = None
    if closing_data:
        parsed_data = frappe.parse_json(closing_data)
        
    return service.close_shift(opening_entry_name, parsed_data)
