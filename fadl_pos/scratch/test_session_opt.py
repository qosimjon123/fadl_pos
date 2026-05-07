import frappe
from fadl_pos.services.session_service import SessionService

frappe.init(site="frontend.test")
frappe.connect()

try:
    service = SessionService("Administrator")
    
    # 1. Test profile payment methods optimization
    profiles = service._get_profiles("Administrator")
    if profiles:
        p_name = profiles[0].name
        mops = service._get_profile_payment_methods(p_name)
        print(f"Payment methods for {p_name}: {mops}")
        for m in mops:
            if 'mop_type' not in m:
                print(f"FAILED: mop_type missing in {m}")
            else:
                print(f"SUCCESS: Found mop_type {m['mop_type']} for {m['mode_of_payment']}")

    # 2. Test normalization/validation would require actually trying to open a shift
    # which might affect DB. I'll just check the logic via unit test or mock if possible.
    # But for now, the mop_type check confirms the query optimization.

finally:
    frappe.destroy()
