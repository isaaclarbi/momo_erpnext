#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import frappe
import base64
import hashlib
import hmac
import json
from frappe import _


def update_paid_requests():
    frappe.log_error('function ran',
                     'new update paid request: Scheduler')
    paystack_profiles = frappe.get_list('Paystack Settings',
            fields=['name'])
    for profile in paystack_profiles:
        doc = frappe.get_doc('Paystack Settings', profile['name'])
        secret_key = doc.get_password(fieldname='secret_key',
                raise_exception=False)

        # Get list of Paystack Transaction Response

        transaction_response_list = \
            frappe.get_list('Transaction Response', fields=['reference'
                            , 'payment_request'])

        # For each unpaid payment request fetch the saved paystack transaction reference

        for transaction_response in transaction_response_list:
            transaction_ref = transaction_response.reference
            pr_id = transaction_response.payment_request

            url = 'https://api.paystack.co/transaction/verify/' \
                + transaction_ref
            headers = {'Authorization': 'Bearer ' + secret_key}
            r = requests.get(url, headers=headers)
            response = r.json()

            if response['status']:
                if response['data']['status'] == 'success':
                    try:

                        # update Payment Request data

                        pr_doc = frappe.get_doc('Payment Request',
                                pr_id)
                    except Exception as e:

                        # pr_doc.create_payment_entry(submit=True)

                        frappe.log_error(str(e),
                                'Updating Payment Request status to SUCCESS'
                                )
                elif response['data']['status'] == 'failed':
                    try:

                        # update Payment Request data

                        pr_doc = frappe.get_doc('Payment Request',
                                pr_id)
                        pr_doc.status = 'Failed'
                        pr_doc.save()
                        frappe.db.commit()
                    except Exception as e:
                        frappe.log_error(str(e),
                                'Updating Payment Request status to FAILED'
                                )
            else:
                frappe.log_error(response['message'],
                                 'Verify Transaction GET Request Error')


    # paystack_profiles = frappe.get_list('Paystack Settings', fields=['name'])
    # for profile in paystack_profiles:
    #     doc = frappe.get_doc('Paystack Settings', profile['name'])
    #     secret_key = doc.get_password(fieldname='secret_key', raise_exception=False)
    #     url =  "https://api.paystack.co/transaction?perPage=100"
    #     headers = {
    #         "Authorization": "Bearer "+ secret_key
    #     }
    #     r = requests.get(url, headers=headers)
    #     response = r.json()
    #     if(response["status"]):
    #         #Get array
    #         transaction_list = response['data']
    #         for transaction in transaction_list:
    #             if(transaction["status"]=="success"):
    #                 pr_id = transaction["metadata"]["payment_request_id"]
    #                 try:
    #                     #Fetch Payment Request that was created
    #                     pr_doc = frappe.get_doc("Payment Request", pr_id)
    #                     #Get Sales Order Document
    #                     so_doc = frappe.get_doc('Sales Order', pr_doc.reference_name)
    #                     # make_sales_invoice(so_doc.name)
    #                     # make_delivery_note(so_doc.name)
    #                     # frappe.db.commit()
    #                     return pr_doc.create_payment_entry(submit=True)
    #                 except Exception as e:
    #                     frappe.log_error(str(e), "Error Creating ")

def verify_request():
    woocommerce_settings = frappe.get_doc('Woocommerce Settings')
    sig = \
        base64.b64encode(hmac.new(woocommerce_settings.secret.encode('utf8'
                         ), frappe.request.data,
                         hashlib.sha256).digest())

    if frappe.request.data \
        and frappe.get_request_header('X-Wc-Webhook-Signature') \
        and not sig \
        == bytes(frappe.get_request_header('X-Wc-Webhook-Signature'
                 ).encode()):
        frappe.throw(_('Unverified Webhook Data'))
    frappe.set_user(woocommerce_settings.creation_user)


@frappe.whitelist(allow_guest=True)
def update_order():
    frappe.log_error('hello','hi')
    # woocommerce_settings = frappe.get_doc("Woocommerce Settings")
    if frappe.request and frappe.request.data:
        frappe.log_error(frappe.request.data,
                         'update_order utils called')
    return "done"
    # ....verify_request()
    # ....try:
    # ........order = json.loads(frappe.request.data)
    # ....except ValueError:
    # ........#woocommerce returns 'webhook_id=value' for the first request which is not JSON
    # ........order = frappe.request.data
    # ....event = frappe.get_request_header("X-Wc-Webhook-Event")

    # else:
    # ....return "success"

    # if event == "updated":
    # ....frappe.log_error(order,'Order Updated')

			