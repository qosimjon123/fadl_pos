# Copyright (c) 2026, FadlTech team and contributors

"""settings controller — wraps ported xpos business logic."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController

from fadl_pos.settings.processing.settings import get_erp_settings as _get_erp_settings
from fadl_pos.settings.processing.settings import get_xpos_branding as _get_xpos_branding
from fadl_pos.settings.processing.settings import get_currencies as _get_currencies
from fadl_pos.settings.processing.settings import get_languages as _get_languages

class SettingsController(BaseController):
	def get_erp_settings(self, *args, **kwargs):
		return _get_erp_settings(*args, **kwargs)

	def get_xpos_branding(self, *args, **kwargs):
		return _get_xpos_branding(*args, **kwargs)

	def get_currencies(self, *args, **kwargs):
		return _get_currencies(*args, **kwargs)

	def get_languages(self, *args, **kwargs):
		return _get_languages(*args, **kwargs)
