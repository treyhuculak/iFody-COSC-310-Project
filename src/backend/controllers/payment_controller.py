from typing import Optional

from fastapi import HTTPException

from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.models.payment import PaymentCreate, PaymentOptions
from src.backend.models.card_payment import CardPaymentCreate
from src.backend.services.payment_service import PaymentService

class PaymentController:
    def __init__(self, repo: Optional[PaymentRepository] = None) -> None:
        self.payment_repo = repo or PaymentRepository()
        self.payment_service = PaymentService()

    def get_payment(self, payment_id: int):
        payment = self.payment_repo.get_payment_by_id(payment_id)
        if payment == None:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        return payment

    def get_payment_methods_by_user_id(self, user_id: int):
        list_of_payments = self.payment_repo.get_payment_methods_by_user_id(user_id)
        if list_of_payments == None:
            raise HTTPException(status_code=404, detail=f"No payment method was found for user id: {user_id}")
        return list_of_payments
    
    def delete_payment_method(self, payment_id: int):
        return self.payment_repo.delete_payment_method(payment_id)

    def add_payment_method(self, payment: CardPaymentCreate | PaymentCreate, active: bool):
        try:
            # Now serialize the payment for storage (if card option was given, serialize card info instead)
            payment_info = None
            if(payment.method == PaymentOptions.CASH):
                payment_info = payment.model_dump(mode="json")
            
            elif (payment.method in [PaymentOptions.CREDIT_CARD, PaymentOptions.DEBIT_CARD]):
                # Ensuring payment parameter has card information
                if not isinstance(payment, CardPaymentCreate):
                    raise ValueError("Card payment data is required.")
                
                # Validating payment/card info
                self.payment_service.validate_payment_logic(payment)
                self.payment_service.define_card_brand(payment)
                    
                payment_info = payment.model_dump(mode="json")
            else:
                raise ValueError("Invalid payment method.")
            
            payment_info['is_active'] = False
            new_payment = self.payment_repo.create_payment_method(payment_info)
            
            if active:
                self.switch_active_payment_method(payment_info['user_id'], new_payment['id'])

                # Just so the return value of this function have the updated version of new_payment
                new_payment['is_active'] = True
            
            return new_payment
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def switch_active_payment_method(self, user_id: int, payment_id: int):
        self.payment_repo.switch_active_payment_method(user_id, payment_id)

    def get_active_payment_method_by_user_id(self, user_id):
        # Retrieving all payment methods for that user
        list_of_methods = self.get_payment_methods_by_user_id(user_id)

        # Finding the first method that is active
        active_method = next(filter(lambda p: p.get("is_active") == True, list_of_methods), None)

        if(active_method == None):
            raise HTTPException(status_code=404, detail=f"No active payment method was found for user id: {user_id}")

        return active_method
