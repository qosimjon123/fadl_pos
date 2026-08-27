# Copyright (c) 2026, FadlTech team and contributors

"""Unit tests for `fadl_pos.login` — pure logic, no Frappe DB/session required."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from fadl_pos.login.constants import QR_PAYLOAD_VERSION
from fadl_pos.login.processing.pin_cipher import decrypt_with_pin, encrypt_with_pin
from fadl_pos.login.serializer import (
	LoginRequest,
	QRGenerateRequest,
	QRLoginRequest,
	QRPayloadRequest,
)


class TestPinCipherRoundTrip(unittest.TestCase):
	def test_encrypt_then_decrypt_returns_original_payload(self):
		payload = {"v": 2, "api_key": "abc123", "api_secret": "secret456"}
		blob = encrypt_with_pin("123456", payload)
		self.assertEqual(decrypt_with_pin("123456", blob), payload)

	def test_two_encryptions_of_same_payload_differ(self):
		payload = {"v": 2, "api_key": "abc123", "api_secret": "secret456"}
		first = encrypt_with_pin("123456", payload)
		second = encrypt_with_pin("123456", payload)
		self.assertNotEqual(first, second)

	def test_decrypt_with_wrong_pin_raises(self):
		blob = encrypt_with_pin("123456", {"v": 2, "api_key": "k", "api_secret": "s"})
		with self.assertRaises(Exception):
			decrypt_with_pin("000000", blob)

	def test_decrypt_tampered_blob_raises(self):
		blob = encrypt_with_pin("123456", {"v": 2, "api_key": "k", "api_secret": "s"})
		tampered = blob[:-3] + ("A" if blob[-3] != "A" else "B") + blob[-2:]
		with self.assertRaises(Exception):
			decrypt_with_pin("123456", tampered)


class TestLoginRequestSerializer(unittest.TestCase):
	def test_accepts_valid_credentials(self):
		body = LoginRequest.model_validate({"usr": "user@example.com", "pwd": "password1"})
		self.assertEqual(body.usr, "user@example.com")

	def test_rejects_short_password(self):
		with self.assertRaises(ValidationError):
			LoginRequest.model_validate({"usr": "user@example.com", "pwd": "short"})

	def test_rejects_unknown_fields(self):
		with self.assertRaises(ValidationError):
			LoginRequest.model_validate({"usr": "user@example.com", "pwd": "password1", "extra": 1})


class TestPinCodeValidator(unittest.TestCase):
	def test_qr_generate_accepts_six_digit_pin(self):
		body = QRGenerateRequest.model_validate({"pin_code": "123456"})
		self.assertEqual(body.pin_code, "123456")

	def test_qr_generate_rejects_non_numeric_pin(self):
		with self.assertRaises(ValidationError):
			QRGenerateRequest.model_validate({"pin_code": "12ab56"})

	def test_qr_generate_rejects_wrong_length_pin(self):
		with self.assertRaises(ValidationError):
			QRGenerateRequest.model_validate({"pin_code": "12345"})

	def test_qr_login_requires_both_fields(self):
		body = QRLoginRequest.model_validate({"encrypted_qr": "x" * 20, "pin_code": "424242"})
		self.assertEqual(body.pin_code, "424242")
		self.assertEqual(body.encrypted_qr, "x" * 20)

	def test_qr_login_rejects_short_encrypted_qr(self):
		with self.assertRaises(ValidationError):
			QRLoginRequest.model_validate({"encrypted_qr": "short", "pin_code": "424242"})


class TestQRPayloadRequest(unittest.TestCase):
	def test_accepts_current_version_payload(self):
		payload = QRPayloadRequest.model_validate(
			{"v": QR_PAYLOAD_VERSION, "api_key": "abc", "api_secret": "secret"}
		)
		self.assertEqual(payload.api_key, "abc")
		self.assertEqual(payload.api_secret, "secret")

	def test_rejects_v1_payload(self):
		with self.assertRaises(ValidationError):
			QRPayloadRequest.model_validate({"v": 1, "api_key": "abc", "api_secret": "secret"})

	def test_rejects_unsupported_version(self):
		with self.assertRaises(ValidationError):
			QRPayloadRequest.model_validate({"v": 99, "api_key": "abc", "api_secret": "secret"})

	def test_rejects_missing_api_secret(self):
		with self.assertRaises(ValidationError):
			QRPayloadRequest.model_validate({"v": QR_PAYLOAD_VERSION, "api_key": "abc"})
