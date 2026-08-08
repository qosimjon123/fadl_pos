# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for `fadl_pos.core` — pure logic, no Frappe DB/session required."""

from __future__ import annotations

import unittest

from pydantic import Field

from fadl_pos.core.events import emit, off, on
from fadl_pos.core.serializer import InputSchema, OutputSchema, dump_out, dump_out_list, validate_in
from fadl_pos.core.workflow import Workflow

INVOICE_TRANSITIONS = {
	"draft": ["submitted", "voided"],
	"submitted": ["paid", "canceled"],
	"paid": [],
	"canceled": [],
	"voided": [],
}


class TestWorkflow(unittest.TestCase):
	def setUp(self):
		self.workflow = Workflow(INVOICE_TRANSITIONS)

	def test_allowed_targets(self):
		self.assertEqual(self.workflow.allowed_targets("draft"), ["submitted", "voided"])
		self.assertEqual(self.workflow.allowed_targets("paid"), [])

	def test_can_transition_allowed(self):
		self.assertTrue(self.workflow.can_transition("draft", "submitted"))
		self.assertTrue(self.workflow.can_transition("submitted", "paid"))

	def test_can_transition_disallowed(self):
		self.assertFalse(self.workflow.can_transition("draft", "paid"))
		self.assertFalse(self.workflow.can_transition("paid", "draft"))

	def test_can_transition_unknown_state(self):
		self.assertFalse(self.workflow.can_transition("unknown", "draft"))

	def test_assert_transition_allowed_is_silent(self):
		self.workflow.assert_transition("draft", "submitted")

	def test_assert_transition_disallowed_raises(self):
		import frappe

		with self.assertRaises(frappe.ValidationError):
			self.workflow.assert_transition("paid", "draft", label="invoice")


class TestEventBus(unittest.TestCase):
	def test_emit_calls_registered_handler_with_payload(self):
		received = {}

		def handler(**payload):
			received.update(payload)

		on("test.core.unit.event")(handler)
		try:
			emit("test.core.unit.event", foo="bar", n=1)
			self.assertEqual(received, {"foo": "bar", "n": 1})
		finally:
			off("test.core.unit.event", handler)

	def test_emit_without_handlers_is_noop(self):
		emit("test.core.unit.no_handlers")

	def test_off_removes_handler(self):
		calls = []

		def handler(**_payload):
			calls.append(1)

		on("test.core.unit.off_event")(handler)
		off("test.core.unit.off_event", handler)
		emit("test.core.unit.off_event")
		self.assertEqual(calls, [])


class _DummyIn(InputSchema):
	name: str = Field(min_length=1)


class _DummyOut(OutputSchema):
	name: str
	shout: bool = False


class TestRpcBoundary(unittest.TestCase):
	def test_validate_in_accepts_valid_payload(self):
		body = validate_in(_DummyIn, {"name": " Alice "})
		self.assertEqual(body.name, "Alice")

	def test_validate_in_rejects_unknown_fields(self):
		import frappe

		with self.assertRaises(frappe.ValidationError):
			validate_in(_DummyIn, {"name": "Alice", "extra": 1})

	def test_dump_out_shapes_dict_result(self):
		out = dump_out(_DummyOut, {"name": "Bob", "shout": True})
		self.assertEqual(out, {"name": "Bob", "shout": True})

	def test_dump_out_is_idempotent_for_non_dict_result(self):
		already_shaped = ["not", "a", "dict"]
		self.assertIs(dump_out(_DummyOut, already_shaped), already_shaped)

	def test_dump_out_list(self):
		out = dump_out_list(_DummyOut, [{"name": "A"}, {"name": "B", "shout": True}])
		self.assertEqual(out, [{"name": "A", "shout": False}, {"name": "B", "shout": True}])
