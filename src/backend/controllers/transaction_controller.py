from typing import Optional

from fastapi import HTTPException

from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.models.payment import PaymentOptions
from src.backend.models.payment_transaction import PaymentTransactionCreate
from src.backend.services.payment_service import PaymentService

class TransactionController:
    def __init__(self, payment_repo: Optional[PaymentRepository] = None, repo: Optional[TransactionRepository] = None) -> None:
        self.payment_repo = payment_repo or PaymentRepository()
        self.transaction_repo = repo or TransactionRepository()
        self.payment_service = PaymentService()

    def get_payment_by_id(self, payment_id: int):
        payment = self.payment_repo.get_payment_by_id(payment_id)
        if payment == None:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return payment
    
    def create_transaction(self, transaction: PaymentTransactionCreate):
        try:
            # Now serialize the payment transaction for storage
            transaction_info = transaction.model_dump(mode="json")
            payment = self.get_payment_by_id(transaction_info['payment_method_id'])

            # Checking payment method
            if(payment['method'] == PaymentOptions.CASH.value):
                transaction_info['is_successful'] = True
            else:
                # Validating payment
                if(self.payment_service.simulate_payment(payment)):
                    transaction_info['is_successful'] = True
                else:
                    transaction_info['is_successful'] = False
                    raise ValueError("Payment was declined.")
                
            return self.transaction_repo.create_transaction(transaction_info)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))