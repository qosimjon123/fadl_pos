# Copyright (c) 2026, FadlTech team and contributors

"""integrations controller — FBR and other external services."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.integrations.processing import fbr as fbr_svc


class IntegrationsController(BaseController):
	def fiscalize_invoice(self, doc):
		return fbr_svc.fiscalize_invoice(doc)

	def prepare_fiscalization(self, doc):
		return fbr_svc.prepare_fiscalization(doc)
