import frappe
import requests

def update_paid_requests():
    frappe.log_error("function ran","update_paid_request: Scheduler")
    paystack_profiles = frappe.get_list('Paystack Settings', fields=['name'])

    #Get list of unconfirmed payment request from ERPNEXT
    unconfirmed_payment_request = frappe.get_list('Payment Request', fields=[''])
    #For each payment request fetch the saved reference

    
    for profile in paystack_profiles:
        doc = frappe.get_doc('Paystack Settings', profile['name'])
        secret_key = doc.get_password(fieldname='secret_key', raise_exception=False)
        url =  "https://api.paystack.co/transaction?perPage=100"
        
        headers = {
            "Authorization": "Bearer "+ secret_key
        }
        r = requests.get(url, headers=headers)
        response = r.json()
        if(response["status"]):
            #Get array
            transaction_list = response['data']
            for transaction in transaction_list:
                if(transaction["status"]=="success"):
                    pr_id = transaction["metadata"]["payment_request_id"]
                    try:
                        #Fetch Payment Request that was created
                        pr_doc = frappe.get_doc("Payment Request", pr_id)
                        #Get Sales Order Document
                        so_doc = frappe.get_doc('Sales Order', pr_doc.reference_name)
                        # make_sales_invoice(so_doc.name)
                        # make_delivery_note(so_doc.name)
                        # frappe.db.commit()
                        return pr_doc.create_payment_entry(submit=True)
                    except frappe.DoesNotExistError:
                        pass

            
