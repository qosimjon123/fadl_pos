# Copyright (c) 2026, FadlTech team and contributors

"""Customer permission guards.

Managing customers has no extra account restrictions beyond the generic
Guest-rejecting gate (any logged-in POS user may search/create/update
customers), so this module simply re-exports the core gate for symmetry with
other feature modules. There is no ``workflow.py`` either: Customer has no
document-status machine in this RPC layer.
"""

from __future__ import annotations

from fadl_pos.core.permission import require_session_user

__all__ = ["require_session_user"]
