# -*- coding: utf-8 -*-
# Copyright (c) 2018, XLevel Retail Systems Nigeria Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json

import frappe
import random
import string
import requests
from paystack.resource import TransactionResource
from frappe import _
from frappe.integrations.utils import create_payment_gateway
from frappe.model.document import Document
from frappe.utils import call_hook_method, nowdate
from requests import RequestException, ConnectionError

SUPPORTED_CURRENCIES = ['GHS']


class PaystackSettings(Document):
	supported_currencies = SUPPORTED_CURRENCIES

	def on_update(self):
		name = 'Paystack-{0}'.format(self.gateway_name)
		create_payment_gateway(
			name,
			settings='Paystack Settings',
			controller=self.gateway_name
		)
		call_hook_method('payment_gateway_enabled', gateway=name)

	def validate_transaction_currency(self, currency):
		if currency not in self.supported_currencies:
			frappe.throw(
				_('{currency} is not supported by Paystack at the moment.').format(currency))

	def get_payment_url(self, **kwargs):
		amount = kwargs.get('amount') * 100
		description = kwargs.get('description')
		slug = kwargs.get('reference_docname')
		email = kwargs.get('payer_email')
		
		metadata = {
			'payment_request': kwargs.get('order_id'),
			'customer_name': kwargs.get('payer_name')
		}


		# secret_key = self.get_password(fieldname='secret_key', raise_exception=False)

		# url = "https://api.paystack.co/transaction/initialize"
		# PARAMS = {
		# 	"address": amount,
		# 	"email": email
		# 	"metadata": metadata
		# }

		# HEADERS = {
		# 	"Authorization": "Bearer "+secret_key,
   		# 	"Cache-Control": "no-cache",
		# }

		# r = requests.post(url, params = PARAMS, headers=HEADERS)
		# res = r.json()
		# return res["data"]["authorization_url"]

		rand = ''.join([random.choice(
            string.ascii_letters + string.digits) for n in range(16)])
		secret_key = self.get_password(fieldname='secret_key', raise_exception=False)
		random_ref = rand
		client = TransactionResource(secret_key, random_ref)
		response = client.initialize(amount*100,email)
		return response['data']['authorization_url']
	
	
	@frappe.whitelist(allow_guest=True)
	def verify_payment(**args):
		# args = frappe._dict(args)
		frappe.log_error("data", "verify payment function called")
		return "done"

		# if(frappe.request and frappe.request.data):
		# 	try:
		# 		data = json.loads(frappe.request.data)
		# 		# if(data["event"]== "paymentrequest.success"):
		# 		frappe.log_error(data, "Paystack Request Data")


		# 	except ValueError:
		# 		#woocommerce returns 'webhook_id=value' for the first request which is not JSON
		# 		data = frappe.request.data
			