import frappe


def get_empty_doc():
	frappe.init(site="development")
	frappe.connect()

	# 1. POS Settings
	pos_settings = frappe.get_single("POS Settings").as_dict()

	# 2. Empty POS Invoice
	doc = frappe.new_doc("POS Invoice")

	# 3. Meta fields
	meta = frappe.get_meta("POS Invoice")
	fields = [
		{"fieldname": f.fieldname, "fieldtype": f.fieldtype}
		for f in meta.fields
		if f.fieldtype not in ("Section Break", "Column Break", "Tab Break", "HTML")
	]

	print(f"POS Settings keys: {list(pos_settings.keys())[:5]}")
	print(f"Empty Invoice keys: {list(doc.as_dict().keys())[:5]}")
	print(f"Number of fields: {len(fields)}")


get_empty_doc()
