from typing import Optional

from fastapi import HTTPException

from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.models.payment import PaymentCreate, PaymentOptions
from src.backend.models.card_payment import CardPaymentCreate, CardPaymentBrand
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

    def add_payment_method(self, payment: CardPaymentCreate | PaymentCreate):
        try:
            # Now serialize the payment for storage (if card option was given, serialize card info instead)
            payment_info = None
            if(payment.method.value == PaymentOptions.CASH.value):
                payment_info = payment.model_dump(mode="json")
            
            elif (payment.method.value == PaymentOptions.CREDIT_CARD.value or payment.method.value == PaymentOptions.DEBIT_CARD.value):
                # Ensuring payment parameter has card information
                if not isinstance(payment, CardPaymentCreate):
                    raise ValueError("Card payment data is required.")
                
                # Validating payment/card info
                self.payment_service.simulate_payment(payment)
                    
                payment_info = payment.model_dump(mode="json")

                if(payment.card_brand.value == CardPaymentBrand.MASTER_CARD.value or payment.card_brand.value == CardPaymentBrand.VISA.value):
                    # FOR NOW, accept all card payments that have a brand
                    payment_info["is_successful"] = True
                else:
                    # FOR NOW, decline all card that do not have a brand
                    payment_info["is_successful"] = False
            else:
                raise ValueError("Invalid payment method.")
            
            return self.payment_repo.create_payment_method(payment_info)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred while adding the payment method.")
        
    def delete_payment_method(self, payment_id: int):
        return self.payment_repo.delete_payment_method(payment_id)
