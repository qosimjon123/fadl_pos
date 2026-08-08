"""Shared service base: session user gate for RPC layers.

The canonical implementation now lives in :mod:`fadl_pos.core.permission`
(``BaseController`` / ``require_session_user``); this module is a thin alias
kept for services that have not moved to the `core/` + `<feature>/` template
yet. New/migrated modules should use ``fadl_pos.core.permission`` directly.
"""

from fadl_pos.core.permission import BaseController as BaseService

__all__ = ["BaseService"]
