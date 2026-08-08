# Copyright (c) 2026, FadlTech team and contributors

"""utilities controller — django-like actions."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.utilities.processing import app_info, helpers


class UtilitiesController(BaseController):
	def get_version_info(self, *args, **kwargs):
		return app_info.get_version_info(*args, **kwargs)

	def get_selling_price_lists(self, *args, **kwargs):
		return app_info.get_selling_price_lists(*args, **kwargs)

	def get_pos_profile_tax_inclusive(self, *args, **kwargs):
		return app_info.get_pos_profile_tax_inclusive(*args, **kwargs)

	def get_active_pos_profile(self, *args, **kwargs):
		return app_info.get_active_pos_profile(*args, **kwargs)

	def get_default_warehouse(self, *args, **kwargs):
		return app_info.get_default_warehouse(*args, **kwargs)

	# helpers formerly exposed via utilities.x_pos
	def get_sales_person_names(self, *args, **kwargs):
		return helpers.get_sales_person_names(*args, **kwargs)

	def get_language_options(self, *args, **kwargs):
		return helpers.get_language_options(*args, **kwargs)

	def get_translation_dict(self, *args, **kwargs):
		return helpers.get_translation_dict(*args, **kwargs)

	def get_database_usage(self, *args, **kwargs):
		return helpers.get_database_usage(*args, **kwargs)

	def get_server_usage(self, *args, **kwargs):
		return helpers.get_server_usage(*args, **kwargs)

	def get_available_languages(self, *args, **kwargs):
		return helpers.get_available_languages(*args, **kwargs)

	def get_current_user_language(self, *args, **kwargs):
		return helpers.get_current_user_language(*args, **kwargs)

	def set_current_user_language(self, *args, **kwargs):
		return helpers.set_current_user_language(*args, **kwargs)

	def get_language_info(self, *args, **kwargs):
		return helpers.get_language_info(*args, **kwargs)

	def log_client_error(self, *args, **kwargs):
		return helpers.log_client_error(*args, **kwargs)
