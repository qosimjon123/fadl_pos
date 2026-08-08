# Copyright (c) 2026, FadlTech team and contributors

"""sales_orders controller — django-like actions."""

from __future__ import annotations

from fadl_pos.core.permission import BaseController
from fadl_pos.sales_orders.processing import orders as orders_svc
from fadl_pos.sales_orders.processing import quotations as quotations_svc


class SalesOrdersController(BaseController):
	def search_orders(self, *args, **kwargs):
		return orders_svc.search_orders(*args, **kwargs)

	def create_sales_order(self, *args, **kwargs):
		return orders_svc.create_sales_order(*args, **kwargs)

	def submit_sales_order(self, *args, **kwargs):
		return orders_svc.submit_sales_order(*args, **kwargs)

	def create_sales_invoice_from_order(self, *args, **kwargs):
		return orders_svc.create_sales_invoice_from_order(*args, **kwargs)

	def create_quotation(self, *args, **kwargs):
		return quotations_svc.create_quotation(*args, **kwargs)

	def submit_quotation(self, *args, **kwargs):
		return quotations_svc.submit_quotation(*args, **kwargs)
