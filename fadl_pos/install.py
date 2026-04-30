# Copyright (c) 2026, FadlTech team and contributors

"""Миграции: кастомные поля на ядровые DocType (User недоступен в Customize Form)."""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
	# update=True — при изменении label/description в коде запись Custom Field в БД обновится
	# (одиночный create_custom_field не трогает уже существующее поле).
	create_custom_fields(
		{
			"User": [
				{
					"fieldname": "qr_encrypted_data",
					"label": "QR Encrypted Data",
					"fieldtype": "Long Text",
					"insert_after": "api_secret",
					"module": "Fadl Pos",
					"description": "Encrypted POS login and permission payload.",
					"print_hide": 1,
					"is_system_generated": 0,
				}
			]
		},
		update=True,
	)
