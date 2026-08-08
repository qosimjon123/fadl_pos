# Copyright (c) 2026, FadlTech team and contributors

"""POS shift session: list / open / close business logic."""

from __future__ import annotations

import frappe
from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
from frappe import _
from frappe.utils import cint
from frappe.utils.data import strip_html

from fadl_pos.core.permission import BaseController
from fadl_pos.session import events
from fadl_pos.session.permission import require_shift_owner
from fadl_pos.session.workflow import assert_can_close


class SessionController(BaseController):
	@staticmethod
	def _required_mop_names(profile_mops: list[dict]) -> set[str]:
		return {
			pm["mode_of_payment"] for pm in profile_mops if cint(pm.get("custom_required_opening_balance"))
		}

	@staticmethod
	def _add_timeline_comment(doc, text: str | None) -> None:
		"""Append a Comment row like Desk timeline (reference_doctype / reference_name)."""
		if not text or not isinstance(text, str):
			return
		cleaned = strip_html(text.strip())
		if not cleaned:
			return

		doc.add_comment("Comment", cleaned)

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
			as_dict=True,
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

	def _fetch_payment_methods(self, profile_names: list[str]) -> list[dict]:
		"""Fetch payment methods for multiple POS Profiles in one query."""
		if not profile_names:
			return []

		rows = frappe.db.sql(
			"""
            SELECT
                pm.parent as pos_profile,
                pm.mode_of_payment,
                pm.default,
                pm.custom_required_opening_balance,
                pm.idx
            FROM
                `tabPOS Payment Method` pm
            WHERE
                pm.parent IN %(profile_names)s AND pm.parenttype = 'POS Profile'
            ORDER BY
                pm.parent ASC, pm.idx ASC
            """,
			{"profile_names": profile_names},
			as_dict=True,
		)
		return rows

	def _fetch_checklists(self, profile_names: list[str]) -> dict[str, dict]:
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
				"disabled": 0,
			},
			fields=["parent", "parentfield", "title", "idx"],
			order_by="idx asc",
		)

		checklists_by_profile: dict[str, dict] = {}
		for item in items:
			p_name = item.parent
			section = "opening" if item.parentfield == "custom_opening_checklist" else "closing"

			if p_name not in checklists_by_profile:
				checklists_by_profile[p_name] = {"opening": [], "closing": []}

			checklists_by_profile[p_name][section].append({"title": item.title})

		return checklists_by_profile

	def _get_profile_config(self, pos_profile: str) -> dict:
		"""Fetch all necessary profile config in minimal queries."""
		return {
			"payment_methods": self._fetch_payment_methods([pos_profile]),
			"allowed_users": frappe.db.get_all("POS Profile User", {"parent": pos_profile}, pluck="user"),
		}

	def _normalize_opening_balances(
		self, profile_mops: list[dict], balance_details: list[dict]
	) -> list[dict]:
		"""All profile MOPs on voucher; required rows from client `name`, others zero."""
		required = self._required_mop_names(profile_mops)
		if not required:
			frappe.throw(
				_("No payment method with Required Opening Balance is configured on this POS Profile.")
			)

		provided: dict[str, float] = {}
		for row in balance_details:
			name = row.get("name")
			if name not in required:
				continue
			provided[name] = frappe.utils.flt(row.get("opening_amount"))

		for mop in required:
			if mop not in provided:
				frappe.throw(_("Please enter an opening balance for {0}").format(mop))

		return [
			{
				"mode_of_payment": pm["mode_of_payment"],
				"opening_amount": provided[pm["mode_of_payment"]]
				if pm["mode_of_payment"] in required
				else 0.0,
			}
			for pm in profile_mops
		]

	def _prepare_closing_reconciliation(
		self,
		closing_entry,
		opening_entry,
		closing_data: list[dict] | None,
		profile_mops: list[dict],
	):
		"""Reconciliation: required MOPs need client closing_amount; others use expected."""
		opening_amounts = {
			d.mode_of_payment: frappe.utils.flt(d.opening_amount) for d in opening_entry.balance_details
		}
		required = self._required_mop_names(profile_mops)
		actual_map: dict[str, float] = {}
		for row in closing_data or []:
			name = row.get("name")
			if name not in required:
				continue
			actual_map[name] = frappe.utils.flt(row.get("closing_amount"))

		existing_mops = []
		for row in closing_entry.payment_reconciliation:
			existing_mops.append(row.mode_of_payment)
			mop = row.mode_of_payment

			opening_amt = opening_amounts.get(mop, 0)
			row.opening_amount = opening_amt
			row.expected_amount += opening_amt

			if mop in required:
				if mop not in actual_map:
					frappe.throw(_("Please enter the closing amount for {0}").format(mop))
				row.closing_amount = actual_map[mop]
			else:
				row.closing_amount = row.expected_amount

			row.difference = frappe.utils.flt(row.closing_amount) - frappe.utils.flt(row.expected_amount)

		for mop, opening_amt in opening_amounts.items():
			if mop in existing_mops:
				continue
			if mop in required and mop not in actual_map:
				frappe.throw(_("Please enter the closing amount for {0}").format(mop))
			closing_amt = actual_map[mop] if mop in required else opening_amt

			closing_entry.append(
				"payment_reconciliation",
				{
					"mode_of_payment": mop,
					"opening_amount": opening_amt,
					"expected_amount": opening_amt,
					"closing_amount": closing_amt,
					"difference": closing_amt - opening_amt,
				},
			)

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
			order_by="period_start_date desc",
		)

	def get_list(self) -> list[dict]:
		"""
		Check for open shifts and fetch POS profile data efficiently.
		If the user already has an open shift, returns that profile immediately (no payment_methods / checklists queries).
		Otherwise all assigned profiles are returned with Close status and opening hints.
		"""
		# 1. Check for open shift immediately (no payment_methods / checklists queries)
		open_shift = self._check_opening_entry(self.user)
		active_entry = open_shift[0] if open_shift else None

		if active_entry:
			return [
				{
					"pos_profiles": [
						{
							"name": active_entry.pos_profile,
							"status": "Open",
							"company": active_entry.company,
							"opening_entry": active_entry.name,
							"opening_entry_date": active_entry.period_start_date,
						}
					]
				}
			]

		profiles = self._get_profiles(self.user)

		profile_names = [p.get("name") for p in profiles]

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

			profile_dict = {
				"name": p_name,
				"status": "Close",
				"company": company,
				"opening_entry": None,
			}

			profile_mops = mops_by_profile.get(p_name, [])

			payment_methods = []
			for pm in profile_mops:
				if not cint(pm.get("custom_required_opening_balance")):
					continue
				payment_methods.append({"name": pm["mode_of_payment"]})

			profile_dict["checklists"] = [checklists_by_profile.get(p_name, {"opening": [], "closing": []})]
			profile_dict["payment_methods"] = payment_methods

			pos_profiles_response.append(profile_dict)

		return [{"pos_profiles": pos_profiles_response}]

	def open_shift(
		self,
		pos_profile: str,
		company: str,
		balance_details: list[dict],
		comment: str | None = None,
	) -> list[dict]:
		"""Create a new POS Opening Entry (open shift)."""
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
				frappe.throw(
					_("You already have an open POS shift. Please close it before opening a new one.")
				)
			if entry.pos_profile == pos_profile:
				frappe.throw(
					_("POS Profile {0} is already in use by another cashier.").format(
						frappe.bold(pos_profile)
					)
				)

		config = self._get_profile_config(pos_profile)
		allowed_users = config["allowed_users"]
		if allowed_users and self.user not in allowed_users:
			frappe.throw(_("User {0} is not allowed to use POS Profile {1}").format(self.user, pos_profile))

		normalized_details = self._normalize_opening_balances(config["payment_methods"], balance_details)

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
		new_pos_opening.set("balance_details", normalized_details)
		new_pos_opening.submit()
		if comment:
			self._add_timeline_comment(new_pos_opening, comment)

		events.shift_opened(user=self.user, pos_profile=pos_profile, opening_entry=new_pos_opening.name)

		return self.get_list()

	def close_shift(
		self,
		opening_entry_name: str,
		closing_data: list[dict] | None = None,
		comment: str | None = None,
	) -> dict:
		"""
		Create and submit a POS Closing Entry from an opening entry.
		"""
		opening_entry = frappe.get_doc("POS Opening Entry", opening_entry_name)

		assert_can_close(opening_entry.status)
		require_shift_owner(opening_entry.user, self.user)

		# 1. Generate closing entry using native builder
		closing_entry = make_closing_entry_from_opening(opening_entry)

		config = self._get_profile_config(opening_entry.pos_profile)
		self._prepare_closing_reconciliation(
			closing_entry, opening_entry, closing_data, config["payment_methods"]
		)

		# 3. Save and submit
		closing_entry.insert(ignore_permissions=True)
		closing_entry.submit()

		# Reload to capture status change
		closing_entry.load_from_db()

		if comment:
			self._add_timeline_comment(closing_entry, comment)

		events.shift_closed(
			user=self.user, opening_entry=opening_entry.name, closing_entry=closing_entry.name
		)

		return {
			"status": "success" if closing_entry.status in ["Submitted", "Queued"] else "failed",
			"is_final": bool(closing_entry.status == "Submitted"),
			"entry_status": closing_entry.status,
			"closing_entry": closing_entry.name,
			"error_message": closing_entry.error_message if closing_entry.status == "Failed" else None,
		}
