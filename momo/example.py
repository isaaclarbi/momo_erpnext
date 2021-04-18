import requests

url =  "https://api.paystack.co/transaction/verify/"+"jv5buhzo4d"
secret_key = "sk_test_263963288e790e94b572398d0ee801a57e0a7b9c"
headers = {
        "Authorization": "Bearer "+secret_key
    }
r = requests.get(url, headers=headers)
response = r.json()
# print(response)

if(response["status"]):
    if(response["data"]["status"]=="success"):
        print(response["data"]["metadata"]["order_id"],'order_id verified')
else:
    print(response.message or 'Verification call to Paystack Failed', "Verification call to Paystack Failed")