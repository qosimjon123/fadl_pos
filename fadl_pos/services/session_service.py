from typing import TypedDict, List
import frappe
from frappe import _

from fadl_pos.services._base import BaseService

from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening

from fadl_pos.serializers.session import (
    SessionListResponseSerializer,
    ClosingReconciliationItem,
    CloseShiftResponse,
    BalanceDetailItem,
    InternalPaymentMethod,
    Checklists
)

class SessionService(BaseService):

    def _get_profiles(self, user):
        """
        Rewrited native pos_profile_query logic:
        1. Profiles where user is explicitly listed.
        2. Profiles where NO users are listed (accessible to everyone).
        """
        # Profiles assigned to user
        user_profiles = frappe.db.sql(
            """
            SELECT pf.name, pf.company
            FROM `tabPOS Profile` pf
            INNER JOIN `tabPOS Profile User` pfu ON pfu.parent = pf.name
            WHERE pfu.user = %(user)s AND pf.disabled = 0
            """,
            {"user": user},
            as_dict=True
        )

        # Profiles with NO users (everyone) 
        # TODO for now we skip this point
        # public_profiles = frappe.db.sql(
        #     """
        #     SELECT pf.name, pf.company
        #     FROM `tabPOS Profile` pf
        #     LEFT JOIN `tabPOS Profile User` pfu ON pfu.parent = pf.name
        #     WHERE pfu.user IS NULL AND pf.disabled = 0
        #     """,
        #     as_dict=True
        # )
        
        return user_profiles

    def _validate_applicable_user(self, pos_profile: str, allowed_users: List[str]):
        """
        Validate if the user is allowed to use this POS Profile based on pre-fetched list.
        """
        if allowed_users and self.user not in allowed_users:
            frappe.throw(_("User {0} is not allowed to use POS Profile {1}").format(
                self.user, pos_profile
            ))

    def _fetch_payment_methods(self, profile_names: List[str]) -> List[InternalPaymentMethod]:
        """
        Fetch payment methods for multiple POS Profiles including their type in ONE query.
        """
        if not profile_names:
            return []

        return frappe.db.sql(
            """
            SELECT 
                pm.parent as pos_profile, pm.mode_of_payment, pm.default, mop.type as mop_type
            FROM 
                `tabPOS Payment Method` pm
            JOIN 
                `tabMode of Payment` mop ON mop.name = pm.mode_of_payment
            WHERE 
                pm.parent IN %(profile_names)s AND pm.parenttype = 'POS Profile'
            """,
            {"profile_names": profile_names},
            as_dict=True
        )

    def _fetch_checklists(self, profile_names: List[str]) -> dict[str, Checklists]:
        """
        Fetch all checklists for multiple POS Profiles in ONE query, preserving order via idx.
        """
        if not profile_names:
            return {}

        items = frappe.db.get_all(
            "POS Checklist Item",
            filters={
                "parent": ["in", profile_names],
                "parentfield": ["in", ["custom_opening_checklist", "custom_closing_checklists"]],
                "disabled": 0
            },
            fields=["parent", "parentfield", "title", "idx"],
            order_by="idx asc"
        )

        checklists_by_profile: dict[str, Checklists] = {}
        for item in items:
            p_name = item.parent
            section = "opening" if item.parentfield == "custom_opening_checklist" else "closing"
            
            if p_name not in checklists_by_profile:
                checklists_by_profile[p_name] = {"opening": [], "closing": []}
            
            checklists_by_profile[p_name][section].append({"title": item.title})
            
        return checklists_by_profile

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
        
    def _validate_shift_availability(self, pos_profile: str):
        """
        Check if user or profile already has an open shift in ONE query.
        """
        open_entries = frappe.db.get_all(
            "POS Opening Entry",
            filters={
                "pos_closing_entry": ["in", ["", None]],
                "docstatus": 1,
            },
            or_filters=[
                ["user", "=", self.user],
                ["pos_profile", "=", pos_profile],
            ],
            fields=["user", "pos_profile"],
        )
        for entry in open_entries:
            if entry.user == self.user:
                 frappe.throw(_("You already have an open POS shift. Please close it before opening a new one."))
            if entry.pos_profile == pos_profile:
                frappe.throw(_("POS Profile {0} is already in use by another cashier.").format(frappe.bold(pos_profile)))

    def _get_profile_config(self, pos_profile: str) -> dict:
        """Fetch all necessary profile config in minimal queries."""
        return {
            "payment_methods": self._fetch_payment_methods([pos_profile]),
            "allowed_users": frappe.db.get_all("POS Profile User", {"parent": pos_profile}, pluck="user")
        }

    def _normalize_opening_balances(self, profile_mops: List[InternalPaymentMethod], balance_details: List[BalanceDetailItem]) -> List[dict]:
        """Validates Cash requirements and filters out non-Cash methods."""
        provided_mops = {d.get("mode_of_payment"): d.get("opening_amount") for d in balance_details}
        
        normalized_details: List[dict] = []
        for pm in profile_mops:
            if pm.get("mop_type") == "Cash":
                mop = pm.get("mode_of_payment")
                amount = provided_mops.get(mop)
                
                if amount is None or amount == "":
                    frappe.throw(_("Please enter an opening balance for Cash ({0}) as required by POS Profile").format(mop))
                
                normalized_details.append({
                    "mode_of_payment": mop,
                    "opening_amount": frappe.utils.flt(amount)
                })
        return normalized_details

    def _prepare_closing_reconciliation(self, closing_entry, opening_entry, closing_data):
        """Processes the reconciliation table for a closing entry efficiently."""
        opening_amounts = {d.mode_of_payment: frappe.utils.flt(d.opening_amount) for d in opening_entry.balance_details}
        actual_map = {p.get("mode_of_payment"): p.get("closing_amount") for p in (closing_data or [])}
        
        # Collect all MOPs to fetch their types in one query
        all_mops = set(list(opening_amounts.keys()) + [row.mode_of_payment for row in closing_entry.payment_reconciliation])
        mop_types = {m.name: m.type for m in frappe.get_all("Mode of Payment", filters={"name": ["in", list(all_mops)]}, fields=["name", "type"])}

        existing_mops = []
        for row in closing_entry.payment_reconciliation:
            existing_mops.append(row.mode_of_payment)
            
            opening_amt = opening_amounts.get(row.mode_of_payment, 0)
            row.opening_amount = opening_amt
            row.expected_amount += opening_amt
            
            mop_type = mop_types.get(row.mode_of_payment)
            
            if row.mode_of_payment in actual_map and actual_map[row.mode_of_payment] is not None:
                row.closing_amount = frappe.utils.flt(actual_map[row.mode_of_payment])
            elif mop_type == "Cash":
                frappe.throw(_("Please enter the actual closing amount for Cash ({0})").format(row.mode_of_payment))
            else:
                row.closing_amount = row.expected_amount
            
            row.difference = frappe.utils.flt(row.closing_amount) - frappe.utils.flt(row.expected_amount)
                
        # Append payment methods that were in the opening entry but had NO transactions
        for mop, opening_amt in opening_amounts.items():
            if mop not in existing_mops:
                mop_type = mop_types.get(mop)
                closing_amt = opening_amt
                
                if mop in actual_map and actual_map[mop] is not None:
                    closing_amt = frappe.utils.flt(actual_map[mop])
                elif mop_type == "Cash":
                     frappe.throw(_("Please enter the actual closing amount for Cash ({0})").format(mop))

                closing_entry.append("payment_reconciliation", {
                    "mode_of_payment": mop,
                    "opening_amount": opening_amt,
                    "expected_amount": opening_amt,
                    "closing_amount": closing_amt,
                    "difference": closing_amt - opening_amt
                })

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
        Check for open shifts and fetch POS profile data efficiently.
        """
        profiles = self._get_profiles(self.user)
        profile_names = [p.get("name") for p in profiles]
        
        # 1. Fetch all open vouchers for user in one query
        open_vouchers = self._check_opening_entry(self.user)
        active_entry = open_vouchers[0] if open_vouchers else None

        # 2. Fetch all payment methods for all profiles in one batch query
        all_mops = self._fetch_payment_methods(profile_names)
        
        mops_by_profile = {}
        for mop in all_mops:
            mops_by_profile.setdefault(mop.pos_profile, []).append(mop)

        # 3. Fetch checklists for all profiles (Optimization: ONE query, preserves order)
        checklists_by_profile = self._fetch_checklists(profile_names)

        pos_profiles_response = []

        for profile in profiles:
            p_name = profile.get("name")
            company = profile.get("company")
            
            # Determine session status
            opening_entry_name = None
            status = "Close"
            if active_entry and active_entry.pos_profile == p_name:
                opening_entry_name = active_entry.name
                status = "Open"

            profile_dict = {
                "name": p_name,
                "status": status,
                "company": company,
                "opening_entry": opening_entry_name,
            }

            # Gather opening requirements for closed shifts
            if status == "Close":
                profile_mops = mops_by_profile.get(p_name, [])
                
                payment_methods = []
                for pm in profile_mops:
                    payment_methods.append({
                        "name": pm.mode_of_payment,
                        "default": pm.default,
                        "type": pm.mop_type,
                        "required_ob": bool(pm.mop_type == "Cash")
                    })

                profile_dict["checklists"] = [
                    checklists_by_profile.get(p_name, {"opening": [], "closing": []})
                ]
                profile_dict["payment_methods"] = payment_methods

            pos_profiles_response.append(profile_dict)

        return [{"pos_profiles": pos_profiles_response}]






    def open_shift(self, pos_profile: str, company: str, balance_details: List[BalanceDetailItem]) -> List[SessionListResponseSerializer]:
        """
        Create a new POS Opening Entry (open shift).
        """
        # 1. Consolidated Availability Check (ONE query for user/profile status)
        self._validate_shift_availability(pos_profile)

        # 2. Get Profile Configuration (Users and Payment Methods)
        config = self._get_profile_config(pos_profile)
        
        # 3. Validate Permission
        self._validate_applicable_user(pos_profile, config["allowed_users"])

        # 4. Normalize and Validate Opening Balances (Strictly Cash)
        normalized_details = self._normalize_opening_balances(config["payment_methods"], balance_details)

        # 5. Create Opening Voucher
        self._create_opening_voucher(pos_profile, company, normalized_details)
        
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

        # 1. Generate closing entry using native builder
        closing_entry = make_closing_entry_from_opening(opening_entry)
        
        # 2. Merge and Fix Reconciliation logic (Extracted)
        self._prepare_closing_reconciliation(closing_entry, opening_entry, closing_data)
        
        # 3. Save and submit
        closing_entry.insert(ignore_permissions=True)
        closing_entry.submit()
        
        # Reload to capture status change
        closing_entry.load_from_db()
        
        return {
            "status": "success" if closing_entry.status in ["Submitted", "Queued"] else "failed",
            "is_final": bool(closing_entry.status == "Submitted"),
            "entry_status": closing_entry.status,
            "closing_entry": closing_entry.name,
            "error_message": closing_entry.error_message if closing_entry.status == "Failed" else None
        }
