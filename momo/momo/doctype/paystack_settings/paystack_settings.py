from __future__ import unicode_literals
import frappe
from frappe import _
import json
import requests
from frappe.integrations.utils import create_payment_gateway
from frappe.model.document import Document
from frappe.utils import call_hook_method, nowdate
# import random
# import string
# from paystack.resource import TransactionResource

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
        secret_key = self.get_password(
            fieldname='secret_key', raise_exception=False)
        amount = kwargs.get('amount') * 100
        description = kwargs.get('description')
        reference = kwargs.get('reference_docname')
        email = kwargs.get('payer_email')

        url = "https://api.paystack.co/transaction/initialize/"
        # metadata = {
        #     'payment_request': kwargs.get('order_id'),
        #     'customer_name': kwargs.get('payer_name')
        # }
        headers = {
            "Authorization": "Bearer "+secret_key,
            "Cache-Control": "no-cache",
            "Content-Type": "application/json"
        }
        data = {
            "amount": amount,
            "currency": "GHS",
            "email": email,
            "metadata": {
                "order_id": reference
            }
        }

        r = requests.post(url, data=json.dumps(data), headers=headers)
        res_json = r.json()
        print(res_json)

        successful = res_json['status'] == True
        failed = res_json['status'] == False
        if(successful):
            authorization_url = res_json['data']['authorization_url']
            return authorization_url
        elif(failed):
            frappe.throw("Request failed with message: " + res_json['message'])

        # Use paystakk package
        # rand = ''.join([random.choice(
    #     string.ascii_letters + string.digits) for n in range(16)])
        # secret_key = self.get_password(fieldname='secret_key', raise_exception=False)
        # random_ref = rand
        # client = TransactionResource(secret_key, random_ref)
        # response = client.initialize(amount,email)
        # return response['data']['authorization_url']


@frappe.whitelist(allow_guest=True)
def verify_payment():
    # Use this if you call the method via get url https://kellypee.theadvisorylab.net/api/method/erpnext.accounts.doctype.payment_request.payment_request.make_payment_request?dn=SAL-ORD-2021-00002&dt=Sales%20Order&submit_doc=1&order_type=Shopping%20Cart
    # def verify_payment(**args):
    # args = frappe._dict(args)
    # ref_doc = frappe.get_doc(args.dt, args.dn)
    if(frappe.request and frappe.request.data):
        res = json.loads(frappe.request.data)
        if(res["event"] == "paymentrequest.success"):
            frappe.local.response['http_status_code'] = 200 
			frappe.log_error(json.dumps(res["data"]["metadata"]["order_id"]),'paymentrequest.success')
            
        else:
            pass
    else:
        return frappe.throw("No data")

#use postman to send a simulated paystack success event and write the logic to update the appropriate sale order.
		#write another function to run and release held up stocks after a set time
        #Return res 200 for paystack to stop sending webhook event