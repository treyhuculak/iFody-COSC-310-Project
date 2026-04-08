from typing import Optional

from fastapi import HTTPException

from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.models.payment import PaymentOptions
from src.backend.models.payment_transaction import PaymentTransactionCreate
from src.backend.services.payment_service import PaymentService
from src.backend.controllers.notification_controller import NotificationController
from src.backend.services.paypal_service import PayPalService

class PayPalController:
    def __init__(
            self, 
            payment_repo: Optional[PaymentRepository] = None, 
            repo: Optional[TransactionRepository] = None, 
            notif_controller: Optional[NotificationController] = None
        ) -> None:
        
        self.payment_repo = payment_repo or PaymentRepository()
        self.transaction_repo = repo or TransactionRepository()
        self.notif_controller = notif_controller or NotificationController()
        self.payment_service = PaymentService()
        self.paypal_service = PayPalService()

    def _get_payment_by_id(self, payment_id: int):
        payment = self.payment_repo.get_payment_by_id(payment_id)
        if payment == None:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return payment

    def start_paypal_transaction(self, transaction: PaymentTransactionCreate):
        try:
            # Now serialize the payment transaction for storage
            transaction_info = transaction.model_dump(mode="json")
            payment = self._get_payment_by_id(transaction_info['payment_method_id'])

            # Ensure payment method is PayPal
            if payment["method"] != PaymentOptions.PAYPAL.value:
                raise HTTPException(status_code=400, detail=f"PayPal payment method not found")

            paypal_order = self.paypal_service.create_order(amount=transaction_info["amount"], user_id=payment["user_id"], currency_code="CAD")

            # Populating the transaction/paypal variable with the necessary fields
            transaction_info['provider_order_id'] = paypal_order.provider_order_id
            transaction_info['provider_status'] = paypal_order.provider_status
            transaction_info["links"] = [link.model_dump() for link in paypal_order.links]
            transaction_info['approve_url'] = self.paypal_service.get_approve_link(paypal_order)
            transaction_info['user_id'] = payment['user_id']

            # Just a placeholder for now
            transaction_info['is_successful'] = False
                
            return self.transaction_repo.create_transaction(transaction_info)
        
        except HTTPException as e:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def capture_paypal_transaction(self, transaction_id: int):
        try:
            transaction = self.transaction_repo.get_transaction_by_id(transaction_id)

            capture_data = self.paypal_service.capture_order(transaction["provider_order_id"])

            transaction['provider_status'] = capture_data['status']

            if capture_data['status'] == "COMPLETED":
                transaction["is_successful"] = True
                return self.transaction_repo.update_transaction(transaction_id, transaction)
            else:
                transaction["is_successful"] = False
                raise HTTPException(status_code=400, detail=f"PayPal payment not completed")
        
        except HTTPException as e:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))