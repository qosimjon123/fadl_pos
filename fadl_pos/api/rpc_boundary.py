# Copyright (c) 2026, FadlTech team and contributors

"""Frappe RPC boundary: validate In models, normalize Out.

The canonical implementation now lives in :mod:`fadl_pos.core.serializer`; this
module is a thin re-export kept for the feature modules that have not moved to
the `core/` + `<feature>/` template yet (``session.py``, ``invoice.py``,
``catalog.py``, ``customer.py``, ``stock.py``, ``offers.py``, ``payment.py``,
``invoice_list.py``). New/migrated modules should import from
``fadl_pos.core.serializer`` directly.
"""

from __future__ import annotations

from fadl_pos.core.errors import validation_error as raise_validation_error
from fadl_pos.core.serializer import InputSchema, OutputSchema, dump_out, dump_out_list, validate_in

__all__ = [
	"InputSchema",
	"OutputSchema",
	"dump_out",
	"dump_out_list",
	"raise_validation_error",
	"validate_in",
]
