import requests
import base64
from datetime import datetime
from requests.auth import HTTPBasicAuth

class MpesaSTK:
    def __init__(self, consumer_key, consumer_secret, shortcode, passkey, callback_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.passkey = passkey
        self.callback_url = callback_url
        self.base_url = "https://sandbox.safaricom.co.ke"  # Sandbox for testing

    def get_access_token(self):
        """
        Step 1: Get access token from Safaricom API
        """
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        access_token = response.json().get("access_token")
        return access_token

    def lipa_na_mpesa_online(self, phone_number, amount, account_reference="TestPayment", transaction_desc="Payment"):
        """
        Step 2: Make STK Push request
        """
        access_token = self.get_access_token()
        api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        # Generate timestamp → format: YYYYMMDDHHMMSS
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # Generate password = base64(shortcode + passkey + timestamp)
        password = base64.b64encode(
            (self.shortcode + self.passkey + timestamp).encode("utf-8")
        ).decode("utf-8")

        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",  # or "CustomerBuyGoodsOnline"
            "Amount": amount,
            "PartyA": phone_number,     # Phone number paying
            "PartyB": self.shortcode,   # Till/Paybill
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()
