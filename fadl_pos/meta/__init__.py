from fadl_pos.meta.main import CUSTOMER_FIELDS as _CUSTOMER_FIELDS_MAP
from fadl_pos.meta.main import POS_PROFILE_FIELDS as _POS_PROFILE_FIELDS_MAP
from fadl_pos.meta.main import (
	POS_PAYMENT_METHOD_CLIENT_FIELDS,
	POS_PAYMENT_METHOD_SERVER_FIELDS,
)

BOOT_CUSTOMER_FIELDS = tuple(name for name, enabled in _CUSTOMER_FIELDS_MAP.items() if enabled)
BOOT_POS_PROFILE_FIELDS = tuple(name for name, enabled in _POS_PROFILE_FIELDS_MAP.items() if enabled)

# Обратная совместимость: catalog_service импортирует кортеж полей профиля.
POS_PROFILE_FIELDS = BOOT_POS_PROFILE_FIELDS
CUSTOMER_FIELDS = BOOT_CUSTOMER_FIELDS

__all__ = [
	"BOOT_CUSTOMER_FIELDS",
	"BOOT_POS_PROFILE_FIELDS",
	"CUSTOMER_FIELDS",
	"POS_PROFILE_FIELDS",
	"POS_PAYMENT_METHOD_CLIENT_FIELDS",
	"POS_PAYMENT_METHOD_SERVER_FIELDS",
]
