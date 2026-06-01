from datetime import datetime

POS_PROFILE_FIELDS = {
    # ── True: отдаём клиенту (SPA boot) ────────────────────────────────────
    # контекст кассы
    "company": True,  # контекст, склады hardcode
    "currency": True,  # формат сумм
    "customer": True,  # дефолтный клиент (в ответе — развёрнутый doc)
    "name": True,  # id кассы
    "selling_price_list": True,  # цены в каталоге
    "warehouse": True,  # дефолтный склад UI
    # UI каталог и чек
    "action_on_new_invoice": True,  # поведение «новый чек»
    "auto_add_item_to_cart": True,  # автодобавление в корзину
    "hide_images": True,  # скрыть картинки в SPA
    "print_receipt_on_order_complete": True,  # печать после оплаты
    # UI цена, скидка, оплата
    "allow_discount_change": True,  # редактирование скидки
    "allow_partial_payment": True,  # частичная оплата
    "allow_rate_change": True,  # редактирование цены
    "apply_discount_on": True,  # база скидки: Grand Total / Net Total
    "disable_rounded_total": True,  # показ rounded_total (0 = округление вкл.)
    "set_grand_total_to_default_mop": True,  # итог в дефолтный способ оплаты
    # печать и налог (boot)
    "letter_head": True,
    "print_format": True,
    "taxes_and_charges": True,  # empty_invoice.taxes
    # ── False: не в pos_profile boot ──────────────────────────────────────
    # child tables → другие ключи boot
    "applicable_for_users": False,  # login/open_shift
    "custom_closing_checklists": False,  # checklists.closing
    "custom_opening_checklist": False,  # checklists.opening
    "customer_groups": False,  # фильтр Customer API
    "item_groups": False,  # item_groups.tree
    "payments": False,  # opening_voucher.balance_details
    # read-only / фильтры
    "country": False,  # read-only из company
    "disabled": False,  # фильтр get_value (disabled=0)
    # stock и pricing на сервере
    "hide_unavailable_items": False,  # native get_items: SQL по bin.actual_qty на сервере
    "ignore_pricing_rule": False,  # catalog/items API
    "update_stock": False,  # stock ledger
    "validate_stock_on_save": False,  # submit
    # учёт и проводки (только сервер / set_missing_values)
    "account_for_change_amount": False,  # payment entry
    "cost_center": False,
    "expense_account": False,
    "income_account": False,  # set_missing_values
    "project": False,
    "tax_category": False,  # шаблон налогов на сервере
    "write_off_account": False,  # GL / consolidation
    "write_off_cost_center": False,
    "write_off_limit": False,  # closing, не экран продажи
    # печать только на сервере
    "company_address": False,
    "select_print_heading": False,
    "tc_name": False,
    # UTM
    "utm_campaign": False,
    "utm_medium": False,
    "utm_source": False,
}

# Customer — ERPNext Selling + regional/custom (customer_name_in_arabic на сайте UAE).
CUSTOMER_FIELDS = {
    # ── True: SPA (выбор клиента, карта, лояльность) ───────────────────────
    "customer_name": True,  # отображение
    "customer_pos_id": True,  # код карты / QR / штрихкод (Customer POS ID)
    "email_id": True,
    "mobile_no": True,
    "name": True,  # id, поиск
    # ── Идентификация и классификация ──────────────────────────────────────
    "customer_group": False, # для кассы все покупатели это покупатели
    "customer_name_in_arabic": False,  # пока не работаем с арабскими клиентами
    "customer_type": False, # это информация для сервера, не для кассы
    "gender": False, # по имени уже понятно что какой у клиента пол
    "image": False, # может быть в дальнейшем так как это требует ПДн и локальных законов
    "naming_series": False, # это информация для сервера, не для кассы
    "territory": False, # касса это физический магазин, поэтому без разницы из какой территории клиент
    # ── Статус (фильтры Customer API) ──────────────────────────────────────
    "disabled": False,  # Customer API: фильтр disabled=0
    "is_frozen": False, # Customer API: фильтр is_frozen=0
    # ── Контакт и адрес ────────────────────────────────────────────────────
    "customer_primary_address": False,  # есть primary_address # это информация для сервера, не для кассы
    "customer_primary_contact": False,  # есть mobile_no / email_id # это информация для сервера, не для кассы
    "first_name": False,  # read-only из контакта # это информация для сервера, не для кассы
    "last_name": False, # это информация для сервера, не для кассы
    "primary_address": False, # кассе не нужна адреса клиента опять же это ПДн по моему мнению
    # ── Лояльность ─────────────────────────────────────────────────────────
    "loyalty_program": False, # TODO пока убираем пока нет лояльности
    "loyalty_program_tier": False, # TODO пока убираем пока нет лояльности
    # ── Валюта, прайс-лист, банк ───────────────────────────────────────────
    "default_bank_account": False,  # Link Bank Account
    "default_currency": False, # касса работает в одной валюте, поэтому без разницы из какой валюты клиент
    "default_price_list": False, # касса работает с одним прайс-листом, поэтому без разницы из какого прайс-листа клиент
    # ── Налоги ─────────────────────────────────────────────────────────────
    "exempt_from_sales_tax": False,
    "tax_category": False,  # Link Tax Category; Tax Rule при смене клиента
    "tax_id": False, # налог закреплен на уровне кассы, поэтому без разницы из какого налога клиент
    "tax_withholding_category": False,
    "tax_withholding_group": False,
    # ── Учёт, оплата, кредитный лимит ──────────────────────────────────────
    "accounts": False,  # child Party Account # это информация для сервера, не для кассы
    "credit_limits": False,  # это поле реализуется в рамках компании а не клиента
    "payment_terms": False, # это информация для сервера, не для кассы
    # ── Внутренний клиент / связанные компании ─────────────────────────────
    "companies": False,  # child # это информация для сервера, не для кассы
    "is_internal_customer": False, # это информация для сервера, не для кассы
    "represents_company": False, # это информация для сервера, не для кассы
    # ── Продажи, CRM, партнёры, документооборот ────────────────────────────
    "account_manager": False, # это информация для сервера, не для кассы
    "default_commission_rate": False,
    "default_sales_partner": False,  # Link Sales Partner
    "dn_required": False,  # Allow Sales Invoice Creation Without Delivery Note
    "industry": False,  # Link Industry Type
    "lead_name": False, # это информация для сервера, не для кассы
    "market_segment": False,  # Link Market Segment
    "opportunity_name": False,
    "prospect_name": False,
    "sales_team": False,  # child Sales Team
    "so_required": False,  # Allow Sales Invoice Creation Without Sales Order
    # ── Портал, B2B, прочее ─────────────────────────────────────────────────
    "customer_details": False,  # Text; доп. информация о клиенте
    "language": False,  # Link Language; Print Language
    "portal_users": False,  # child
    "supplier_numbers": False,  # child B2B
    "website": False,
}

# Item — ERPNext Stock + custom UAE (tax_code, is_zero_rated, is_exempt); каталог, чек, submit.
ITEM_FIELDS = {
    # ── True: SPA (каталог, карточка, скан, строка POS Invoice) ───────────
    "name": True,  # id / item_code в API (системное; autoname field:item_code)
    "item_code": True,  # код товара
    "item_name": True,  # отображение в каталоге (title_field)
    "item_group": True,  # фильтр, дерево групп
    "tax_code": True,  # custom UAE; налог в строке чека
    "is_zero_rated": True,  # custom UAE; regional/utils.py
    "is_exempt": True,  # custom UAE; освобождение от налога
    "stock_uom": True,  # базовая UOM, остатки
    "sales_uom": True,  # UOM продажи / цена в каталоге
    "disabled": False,  # не показывать в каталоге
    "is_stock_item": True,  # остаток, validate stock
    "is_sales_item": True,  # фильтр каталога (is_sales_item=1)
    "has_batch_no": True,  # выбор batch в UI
    "has_serial_no": True,  # ввод serial в UI
    "has_variants": True,  # шаблон; в списке только has_variants=0
    "variant_of": True,  # вариант шаблона
    "allow_negative_stock": True,  # get_stock_availability
    "allow_alternative_item": True,  # замена в строке
    "image": True,  # каталог (если не hide_images в профиле)
    "description": True,  # карточка, поиск
    "brand": True,  # отображение / фильтр
    "standard_rate": True,  # справочная цена, fallback
    "max_discount": True,  # лимит скидки на строке

    # ── False: child tables → отдельные ключи API / не в slim item doc ─────
    "barcodes": False,  # child Item Barcode; scan API
    "uoms": False,  # child UOM Conversion Detail; get_conversion_factor
    "attributes": False,  # child Item Variant Attribute
    "item_defaults": False,  # child Item Default (company/warehouse)
    "reorder_levels": False,  # child Item Reorder
    "supplier_items": False,  # child Item Supplier
    "customer_items": False,  # child Item Customer Detail
    "taxes": False,  # child Item Tax; налоги на сервере
    # ── False: не для экрана кассы ───────────────────────────────────────
    "naming_series": False,
    "opening_stock": False,  # только при создании Item
    "valuation_rate": False,
    "valuation_method": False,
    "is_fixed_asset": False,  # фильтр каталога (is_fixed_asset=0)
    "asset_category": False,
    "asset_naming_series": False,
    "auto_create_assets": False,
    "is_grouped_asset": False,
    "include_item_in_manufacturing": False,
    "over_delivery_receipt_allowance": False,
    "over_billing_allowance": False,
    "shelf_life_in_days": False,
    "end_of_life": False,
    "default_material_request_type": False,
    "warranty_period": False,
    "weight_per_unit": False,
    "weight_uom": False,
    "create_new_batch": False,
    "batch_number_series": False,
    "has_expiry_date": False,
    "retain_sample": False,
    "sample_quantity": False,
    "serial_no_series": False,
    "variant_based_on": False,
    "is_purchase_item": False,
    "purchase_uom": False,
    "min_order_qty": False,
    "safety_stock": False,
    "lead_time_days": False,
    "last_purchase_rate": False,
    "is_customer_provided_item": False,
    "customer": False,
    "delivered_by_supplier": False,
    "country_of_origin": False,
    "customs_tariff_number": False,
    "grant_commission": False,
    "enable_deferred_revenue": False,
    "no_of_months": False,
    "enable_deferred_expense": False,
    "no_of_months_exp": False,
    "inspection_required_before_purchase": False,
    "inspection_required_before_delivery": False,
    "quality_inspection_template": False,
    "default_bom": False,
    "is_sub_contracted_item": False,
    "production_capacity": False,
    "total_projected_qty": False,  # read-only, hidden
    "customer_code": False,  # hidden; POS Search Fields
    "default_item_manufacturer": False,
    "default_manufacturer_part_no": False,
    "purchase_tax_withholding_category": False,
    "sales_tax_withholding_category": False,
}


if __name__ == "__main__":
    """
        на момент 2026-05-31 в POS_PROFILE_FIELDS:  46
        на момент 2026-05-31 в CUSTOMER_FIELDS:  51
        на момент 2026-05-31 в ITEM_FIELDS:  84
    """
    
    print(f"на момент {datetime.now().strftime('%Y-%m-%d')} в POS_PROFILE_FIELDS: ", len(POS_PROFILE_FIELDS))
    print(f"на момент {datetime.now().strftime('%Y-%m-%d')} в CUSTOMER_FIELDS: ", len(CUSTOMER_FIELDS))
    print(f"на момент {datetime.now().strftime('%Y-%m-%d')} в ITEM_FIELDS: ", len(ITEM_FIELDS))

