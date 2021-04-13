# -*- coding: utf-8 -*-
# Copyright (c) 2021, Isaac larbi and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import random
import string
import frappe
from paystack.resource import TransactionResource
from frappe import _
from frappe.integrations.utils import create_payment_gateway
from frappe.model.document import Document
from frappe.utils import call_hook_method, nowdate
from requests import RequestException, ConnectionError



SUPPORTED_CURRENCIES = ['GHS']

class APIKeys(Document):
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
		amount = kwargs.get('amount')
		description = kwargs.get('description')
		slug = kwargs.get('reference_docname')
		email = kwargs.get('payer_email')
		metadata = {
			'payment_request': kwargs.get('order_id'),
			'customer_name': kwargs.get('payer_name')
		}

		rand = ''.join([random.choice(
            string.ascii_letters + string.digits) for n in range(16)])
		secret_key = self.get_password(fieldname='secret_key', raise_exception=False)
		random_ref = rand
		test_email = email
		test_amount = amount
		plan = 'Basic'
		client = TransactionResource(secret_key, random_ref)
		response = client.initialize(test_amount,
									test_email)
		# print(response)
		return response['data']['authorization_url']


