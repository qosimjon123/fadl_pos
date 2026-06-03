from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InputSchema(BaseModel):
	model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PaginatedQuery(InputSchema):
	limit: int = Field(ge=1, le=100)


class CustomerListQuery(PaginatedQuery):
	search_term: str = ""


class CustomerDetailsQuery(InputSchema):
	customer: str = Field(min_length=1)


class CustomerManageBody(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class BalanceDetailItem(InputSchema):
	name: str = Field(min_length=1)
	opening_amount: float


class ClosingReconciliationItem(InputSchema):
	name: str = Field(min_length=1)
	closing_amount: float


class OpenShiftQuery(InputSchema):
	pos_profile: str = Field(min_length=1)
	company: str = Field(min_length=1)
	comment: str | None = None


class CloseShiftQuery(InputSchema):
	opening_entry_name: str = Field(min_length=1)
	comment: str | None = None


class LoginQuery(InputSchema):
	usr: str = Field(min_length=1)
	pwd: str = Field(min_length=1)


class QRLoginQuery(InputSchema):
	encrypted_qr: str = Field(min_length=1)
	pin_code: str = Field(min_length=1)


class QRGenerateQuery(InputSchema):
	pin_code: str = Field(min_length=1)


class CartLineIn(InputSchema):
	item_code: str = Field(min_length=1)
	qty: float = Field(ge=0)


class CartValidateIn(InputSchema):
	items: list[CartLineIn]
	warehouse: str = Field(min_length=1)


class InvoiceSyncBody(InputSchema):
	model_config = ConfigDict(extra="allow", str_strip_whitespace=True)


class InvoiceListQuery(PaginatedQuery):
	search_term: str = ""
	status: str = "Paid"


BalanceDetailItemType = BalanceDetailItem
ClosingReconciliationItemType = ClosingReconciliationItem
