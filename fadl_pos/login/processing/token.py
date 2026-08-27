# Copyright (c) 2026, FadlTech team and contributors

"""Basic API token issuance and rotation for POS clients."""

from __future__ import annotations

import base64
from dataclasses import dataclass

import frappe
from frappe.model.document import Document


@dataclass(frozen=True)
class BasicToken:
	api_key: str
	api_secret: str

	def as_authorization_header(self) -> str:
		raw = f"{self.api_key}:{self.api_secret}".encode()
		encoded = base64.b64encode(raw).decode("ascii")
		return f"Basic {encoded}"


def ensure_basic_token(doc: Document) -> BasicToken:
	changed = False
	if not doc.api_key:
		doc.api_key = frappe.generate_hash(length=15)
		changed = True

	api_secret = doc.get_password("api_secret", raise_exception=False)
	if not api_secret:
		api_secret = frappe.generate_hash(length=15)
		doc.api_secret = api_secret
		changed = True

	if changed:
		doc.save(ignore_permissions=True)

	return BasicToken(api_key=doc.api_key, api_secret=api_secret)


def rotate_api_secret(doc: Document) -> BasicToken:
	if not doc.api_key:
		doc.api_key = frappe.generate_hash(length=15)
	api_secret = frappe.generate_hash(length=15)
	doc.api_secret = api_secret
	doc.save(ignore_permissions=True)
	return BasicToken(api_key=doc.api_key, api_secret=api_secret)
