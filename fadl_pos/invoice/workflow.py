# Copyright (c) 2026, FadlTech team and contributors

"""Invoice document state machine helpers."""

from __future__ import annotations

from fadl_pos.core.workflow import Workflow

INVOICE_TRANSITIONS = {
	"draft": ["submitted", "voided"],
	"submitted": ["paid", "canceled"],
	"paid": [],
	"canceled": [],
	"voided": [],
}

invoice_workflow = Workflow(INVOICE_TRANSITIONS)
