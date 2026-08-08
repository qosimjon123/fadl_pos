# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for `fadl_pos.login` — pure logic, no Frappe DB/session required."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from fadl_pos.login.pin_cipher import decrypt_with_pin, encrypt_with_pin
from fadl_pos.login.serializer import (
	LoginQuery,
	QRGenerateQuery,
	QRLoginQuery,
	QRPayloadIn,
)


class TestPinCipherRoundTrip(unittest.TestCase):
	def test_encrypt_then_decrypt_returns_original_payload(self):
		payload = {"v": 1, "api_key": "abc123", "qr_token": "x" * 32}
		blob = encrypt_with_pin("123456", payload)
		self.assertEqual(decrypt_with_pin("123456", blob), payload)

	def test_two_encryptions_of_same_payload_differ(self):
		payload = {"v": 1, "api_key": "abc123", "qr_token": "x" * 32}
		first = encrypt_with_pin("123456", payload)
		second = encrypt_with_pin("123456", payload)
		self.assertNotEqual(first, second)

	def test_decrypt_with_wrong_pin_raises(self):
		blob = encrypt_with_pin("123456", {"v": 1, "api_key": "k", "qr_token": "x" * 32})
		with self.assertRaises(Exception):
			decrypt_with_pin("000000", blob)

	def test_decrypt_tampered_blob_raises(self):
		blob = encrypt_with_pin("123456", {"v": 1, "api_key": "k", "qr_token": "x" * 32})
		tampered = blob[:-3] + ("A" if blob[-3] != "A" else "B") + blob[-2:]
		with self.assertRaises(Exception):
			decrypt_with_pin("123456", tampered)


class TestLoginQuerySerializer(unittest.TestCase):
	def test_accepts_valid_credentials(self):
		body = LoginQuery.model_validate({"usr": "user@example.com", "pwd": "password1"})
		self.assertEqual(body.usr, "user@example.com")

	def test_rejects_short_password(self):
		with self.assertRaises(ValidationError):
			LoginQuery.model_validate({"usr": "user@example.com", "pwd": "short"})

	def test_rejects_unknown_fields(self):
		with self.assertRaises(ValidationError):
			LoginQuery.model_validate({"usr": "user@example.com", "pwd": "password1", "extra": 1})


class TestPinCodeValidator(unittest.TestCase):
	def test_qr_generate_accepts_six_digit_pin(self):
		body = QRGenerateQuery.model_validate({"pin_code": "123456"})
		self.assertEqual(body.pin_code, "123456")

	def test_qr_generate_rejects_non_numeric_pin(self):
		with self.assertRaises(ValidationError):
			QRGenerateQuery.model_validate({"pin_code": "12ab56"})

	def test_qr_generate_rejects_wrong_length_pin(self):
		with self.assertRaises(ValidationError):
			QRGenerateQuery.model_validate({"pin_code": "12345"})

	def test_qr_login_requires_both_fields(self):
		body = QRLoginQuery.model_validate({"encrypted_qr": "x" * 20, "pin_code": "424242"})
		self.assertEqual(body.pin_code, "424242")
		self.assertEqual(body.encrypted_qr, "x" * 20)

	def test_qr_login_rejects_short_encrypted_qr(self):
		with self.assertRaises(ValidationError):
			QRLoginQuery.model_validate({"encrypted_qr": "short", "pin_code": "424242"})


class TestQRPayloadIn(unittest.TestCase):
	def test_accepts_current_version_payload(self):
		payload = QRPayloadIn.model_validate({"v": 1, "api_key": "abc", "qr_token": "x" * 32})
		self.assertEqual(payload.api_key, "abc")

	def test_rejects_unsupported_version(self):
		with self.assertRaises(ValidationError):
			QRPayloadIn.model_validate({"v": 2, "api_key": "abc", "qr_token": "x" * 32})

	def test_rejects_wrong_qr_token_length(self):
		with self.assertRaises(ValidationError):
			QRPayloadIn.model_validate({"v": 1, "api_key": "abc", "qr_token": "tooshort"})
