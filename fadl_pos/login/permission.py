# Copyright (c) 2026, FadlTech team and contributors

"""Login permission guards.

Password and QR authentication delegate account validation to Frappe's native
``LoginManager`` and ``validate_api_key_secret``. This module only re-exports
the generic session gate for authenticated self-service actions (``generate_qr``,
``clear_sessions``).
"""

from __future__ import annotations

from fadl_pos.core.permission import require_session_user

__all__ = ["require_session_user"]
