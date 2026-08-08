# Copyright (c) 2026, FadlTech team and contributors

"""Pydantic v2 schemas for the customer RPC (search / CRUD / addresses / credit / loyalty)."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import ConfigDict, Field

from fadl_pos.core.serializer import InputSchema, OutputSchema

__all__ = [
	"AddressCreateIn",
	"AddressCreateOut",
	"AddressOut",
	"CustomerCreateIn",
	"CustomerCreateOut",
	"CustomerCreditIn",
	"CustomerCreditRowOut",
	"CustomerDetailsIn",
	"CustomerDetailsOut",
	"CustomerListIn",
	"CustomerLoyaltyProgramOut",
	"CustomerRef",
	"CustomerRowOut",
	"CustomerUpdateIn",
	"CustomerUpdateOut",
	"LoyaltyInfoOut",
	"LoyaltyProgramOut",
	"LoyaltyProgramsIn",
	"LoyaltyRegisterIn",
	"LoyaltyRegisterOut",
	"LoyaltyTierOut",
	"LoyaltyUnenrollOut",
]


class CustomerListIn(InputSchema):
	search_term: str = ""
	limit: int = Field(default=20, ge=1, le=100)
	pos_profile: str | None = None


class CustomerDetailsIn(InputSchema):
	customer: str = Field(min_length=1)


class CustomerRef(InputSchema):
	customer: str = Field(min_length=1)


class CustomerCreateIn(InputSchema):
	customer_name: str = Field(min_length=1)
	mobile_no: str = ""
	email_id: str = ""
	customer_group: str | None = None
	territory: str | None = None
	customer_type: str = "Individual"
	gender: str | None = None
	tax_id: str | None = None
	referral_code: str | None = None
	birthday: str | None = None
	company: str | None = None
	pos_profile: str | None = None
	address_line1: str | None = None
	city: str | None = None
	country: str | None = None


class CustomerUpdateIn(InputSchema):
	model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

	customer: str = Field(min_length=1)
	customer_name: str | None = None
	mobile_no: str | None = None
	email_id: str | None = None
	customer_group: str | None = None
	territory: str | None = None
	customer_type: str | None = None
	gender: str | None = None
	tax_id: str | None = None
	referral_code: str | None = None
	birthday: str | None = None
	discount: float | None = None


class AddressCreateIn(InputSchema):
	customer: str = Field(min_length=1)
	address_title: str | None = None
	address_line1: str | None = None
	address_line2: str | None = None
	city: str | None = None
	state: str | None = None
	country: str | None = None
	pincode: str | None = None
	phone: str | None = None
	is_primary_address: bool = False
	is_shipping_address: bool = False


class CustomerCreditIn(InputSchema):
	customer: str = Field(min_length=1)
	company: str = Field(min_length=1)


class LoyaltyRegisterIn(InputSchema):
	customer: str = Field(min_length=1)
	loyalty_program: str = Field(min_length=1)


class LoyaltyProgramsIn(InputSchema):
	company: str | None = None


class AddressOut(OutputSchema):
	name: str
	address_title: str | None = None
	address_line1: str | None = None
	address_line2: str | None = None
	city: str | None = None
	state: str | None = None
	country: str | None = None
	pincode: str | None = None
	phone: str | None = None
	is_primary_address: int = 0
	is_shipping_address: int = 0


class AddressCreateOut(OutputSchema):
	name: str
	address_title: str | None = None
	address_line1: str | None = None
	city: str | None = None


class CustomerRowOut(OutputSchema):
	name: str
	customer_name: str
	mobile_no: str | None = None
	email_id: str | None = None
	customer_group: str | None = None
	territory: str | None = None
	default_currency: str | None = None
	image: str | None = None
	tax_id: str | None = None
	customer_type: str | None = None
	gender: str | None = None


class CustomerLoyaltyProgramOut(OutputSchema):
	name: str
	loyalty_points: float = 0
	conversion_factor: float = 0


class CustomerDetailsOut(OutputSchema):
	name: str
	customer_name: str
	mobile_no: str | None = None
	email_id: str | None = None
	customer_group: str | None = None
	territory: str | None = None
	default_currency: str | None = None
	default_price_list: str | None = None
	image: str | None = None
	tax_id: str | None = None
	customer_type: str | None = None
	gender: str | None = None
	balance: float = 0
	credit_limit: float = 0
	loyalty_points: float = 0
	loyalty_program: CustomerLoyaltyProgramOut | None = None
	discount: float = 0
	referral_code: str | None = None
	birthday: str | None = None
	addresses: list[AddressOut] = Field(default_factory=list)


class CustomerCreateOut(OutputSchema):
	name: str
	customer_name: str
	mobile_no: str | None = None
	email_id: str | None = None
	customer_group: str | None = None
	territory: str | None = None


class CustomerUpdateOut(OutputSchema):
	name: str
	customer_name: str
	mobile_no: str | None = None
	email_id: str | None = None


class CustomerCreditRowOut(OutputSchema):
	credit_origin: str
	total_credit: float
	type: str
	posting_date: date | datetime | None = None


class SalesPersonOut(OutputSchema):
	name: str
	sales_person_name: str | None = None


class LoyaltyTierOut(OutputSchema):
	tier_name: str
	min_spent: float = 0
	collection_factor: float = 0


class LoyaltyProgramOut(OutputSchema):
	name: str
	loyalty_program_name: str | None = None
	company: str | None = None
	conversion_factor: float = 0
	expiry_duration: int | None = None
	tiers: list[LoyaltyTierOut] = Field(default_factory=list)


class LoyaltyRegisterOut(OutputSchema):
	name: str
	customer_name: str
	loyalty_program: str
	loyalty_program_name: str | None = None
	conversion_factor: float = 0
	loyalty_points: float = 0
	message: str | None = None


class LoyaltyUnenrollOut(OutputSchema):
	name: str
	customer_name: str
	loyalty_program: str | None = None
	message: str | None = None


class LoyaltyInfoOut(OutputSchema):
	enrolled: bool
	customer: str
	customer_name: str
	loyalty_program: str | None = None
	loyalty_program_name: str | None = None
	conversion_factor: float | None = None
	loyalty_points: float | None = None
	points_value: float | None = None
	current_tier: str | None = None
	tiers: list[LoyaltyTierOut] = Field(default_factory=list)
	expiry_duration: int | None = None
