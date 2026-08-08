# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for POS permission catalog constants."""

from __future__ import annotations

import unittest

from fadl_pos.permissions.constants import ALL_PERMISSION_KEYS, DEFAULT_ROLES, POS_PERMISSIONS


class TestPermissionCatalog(unittest.TestCase):
	def test_catalog_unique_and_nonempty(self):
		self.assertGreaterEqual(len(ALL_PERMISSION_KEYS), 10)
		self.assertEqual(len(ALL_PERMISSION_KEYS), len(set(ALL_PERMISSION_KEYS)))
		self.assertEqual(len(POS_PERMISSIONS), len(ALL_PERMISSION_KEYS))

	def test_default_roles_cover_catalog(self):
		names = {name for name, _ in DEFAULT_ROLES}
		self.assertIn("Cashier", names)
		self.assertIn("Manager", names)
		self.assertIn("Administrator", names)
		admin_enabled = dict(DEFAULT_ROLES)["Administrator"]
		self.assertEqual(admin_enabled, set(ALL_PERMISSION_KEYS))
