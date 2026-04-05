import os
import requests
from typing import Any
from dotenv import load_dotenv

from src.backend.models.paypal_payment import PayPalCreate
from src.backend.models.payment import PaymentOptions

'''
This service will handle all the business logic related to paypal transactions, such as getting access token, creating paypal order, and capturing that order. It will interact with the TransactionController for data consistency.
'''

# I should first create a payment with method = paypal (not create a paypal object, instead create a payment object with method = paypal)
# Only create the paypal object for the transaction
load_dotenv()

class PayPalService:
    def __init__(self) -> None:
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.base_url = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")

        if not self.client_id:
            raise ValueError("Missing PAYPAL_CLIENT_ID in environment variables")
        if not self.client_secret:
            raise ValueError("Missing PAYPAL_CLIENT_SECRET in environment variables")

    def get_access_token(self) -> str:
        url = f"{self.base_url}/v1/oauth2/token"

        # Response from getting access token taken from https://developer.paypal.com/api/rest/
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"}
        )

        if response.status_code != 200:
            raise ValueError("Failed to get access token")
        
        data = response.json()
        access_token = data.get("access_token")

        return access_token
    
    def create_order(self, amount: float, user_id: int, transaction_id: int, currency_code: str = "CAD") -> PayPalCreate:
        access_token = self.get_access_token()
        url = f"{self.base_url}/v2/checkout/orders"

        # Response body to create an order taken from https://developer.paypal.com/docs/api/orders/v2/
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "PayPal-Request-Id": f"transaction-{user_id}-{transaction_id}"
            },
            json={
                # Json intent taken from https://developer.paypal.com/api/rest/integration/orders-api/
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                    "amount": {
                        "currency_code": currency_code,
                        "value": str(amount)
                    }
                    }
                ]
            }
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Failed to create PayPal order")
        
        data = response.json()

        return PayPalCreate(
            user_id = user_id,
            method = PaymentOptions.PAYPAL,
            provider_order_id = data.get("id") ,
            provider_status = data.get("status"),
            links = data.get("links")
        )
    
    def capture_order(self, order: PayPalCreate) -> dict[str, Any]:
        access_token = self.get_access_token()
        order_id = order.provider_order_id
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Failed to capture PayPal order")

        data = response.json()
        return data
        
    def get_approve_link(self, order: PayPalCreate) -> str:
        for link in order.links:
            if link.rel == "approve":
                return link.href
        raise ValueError("Approve link not found")