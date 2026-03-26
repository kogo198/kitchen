import requests
import base64
from datetime import datetime
from django.conf import settings

class MpesaClient:
    def __init__(self):
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.shortcode = getattr(settings, 'MPESA_SHORTCODE', '174379')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', '')
        self.base_url = 'https://sandbox.safaricom.co.ke' # Switch to api.safaricom for production

    def get_token(self):
        api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            r = requests.get(api_url, auth=(self.consumer_key, self.consumer_secret))
            return r.json() # Returns dict with 'access_token'
        except Exception:
            return None

    def stk_push(self, phone, amount, reference, desc="Kitchenware Payment"):
        token_data = self.get_token()
        token = token_data.get('access_token') if token_data else None
        
        if not token:
            return {"error": "Failed to authenticate with Safaricom"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(data_to_encode.encode()).decode()
        
        # Phone must be 254...
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = '254' + phone[1:] if phone.startswith('+0') else phone[1:]
        
        # Ensure it starts with 254 and is correct length
        if not phone.startswith('254'):
            phone = '254' + phone[-9:]

        api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": "https://kogo.pythonanywhere.com/shop/mpesa/callback/",
            "AccountReference": reference,
            "TransactionDesc": desc
        }

        try:
            r = requests.post(api_url, json=payload, headers=headers)
            return r.json()
        except Exception as e:
            return {"error": str(e)}
