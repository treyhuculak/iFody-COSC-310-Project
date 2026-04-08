import os
# Documentation for posting HTTP requests: https://www.w3schools.com/python/ref_requests_post.asp
import requests
from typing import Any
from dotenv import load_dotenv
from datetime import datetime 

from src.backend.models.paypal_payment import PayPalCreate

'''
This service will handle all the business logic related to paypal transactions, such as getting access token, creating paypal order, and capturing that order. It will interact with the TransactionController for data consistency.
'''

# I should first create a payment with method = paypal (not create a paypal object, instead create a payment object with method = paypal)
# Only create the paypal object for the transaction
load_dotenv()

class PayPalService:
    def __init__(self) -> None:
        # Grabbing client info from env
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.base_url = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

        '''
        # For debugging purposes
        if not self.client_id:
            raise ValueError("Missing PAYPAL_CLIENT_ID in environment variables")
        if not self.client_secret:
            raise ValueError("Missing PAYPAL_CLIENT_SECRET in environment variables")
            '''
        
    '''
    Helper function to get the access token for the business account
    '''
    def _get_access_token(self) -> str:
        url = f"{self.base_url}/v1/oauth2/token"

        # Response format from "getting access token" taken from https://developer.paypal.com/api/rest/
        response = requests.post(
            url,
            auth=(self.client_id, self.client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"}, # Expliciting the format the API will receive this request information
            data={"grant_type": "client_credentials"}
        )

        if response.status_code != 200:
            raise ValueError("Failed to get access token")
        
        data = response.json()
        access_token = data.get("access_token")

        return access_token
    
    
    def create_order(self, amount: float, user_id: int, currency_code: str = "CAD") -> PayPalCreate:
        access_token = self._get_access_token()
        url = f"{self.base_url}/v2/checkout/orders"

        # Response body to "create an order" taken from https://developer.paypal.com/docs/api/orders/v2/ - confirm & create order section
        # (only used the necessary json information to make this work)
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "PayPal-Request-Id": f"transaction-{user_id}-{datetime.now().isoformat()}" # Making sure no duplicate transactions happen
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
                ],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            # Links to where the user should be sent after clicking the confirmation/return paypal button and the cancel paypal button
                            # Also grabbed from https://developer.paypal.com/docs/api/orders/v2/ confirm order section
                            "return_url": f"{self.frontend_url}/?paypal_status=approved&paypal_message=PayPal%20approval%20completed",
                            "cancel_url": f"{self.frontend_url}/?paypal_status=cancelled&paypal_message=PayPal%20payment%20was%20cancelled.",
                            "user_action": "PAY_NOW"
                        }
                    }
                }
            }
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Failed to create PayPal order")
        
        data = response.json()

        return PayPalCreate(provider_order_id = data.get("id"), provider_status = data.get("status"), links = data.get("links"))
    
    def capture_order(self, order_id: str) -> dict[str, Any]:
        access_token = self._get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )

        if response.status_code not in (200, 201):
            raise ValueError(f"Failed to capture PayPal order")

        data = response.json()
        return data
        
    def get_approve_link(self, paypal_order: PayPalCreate) -> str:
        flag = False

        # Note: paypal_order and the paypal links object are both pydantic (not dict)
        for link in paypal_order.links:
            # Fetch the purpose (what it does conceptually) of the href link
            rel = link.rel
            # Fetch the href url itself
            href = link.href

            # Paypal documentation usually have approve as the rel string, but some newer doc says to use payer-action
            if rel in {"payer-action", "approve"}:
                flag = True
                break

        if not flag:
            raise ValueError("Approve link not found")
            
        return href
            