from datetime import datetime

from fastapi import HTTPException
from src.backend.models.card_payment import CardPaymentCreate, CardPaymentBrand #, CardPaymentResponse

'''
This service will handle all the business logic related to payment, such as validating card input. It will interact with the PaymentController for data consistency.
'''

class PaymentService:

    def __init__(self):
        pass

    # Call this function when updating the status to payment confirmed
    def simulate_payment(self, payment_data: CardPaymentCreate) -> bool: # # Maybe put this as CardPaymentResponse
        # Define and validate functions maybe can be called by the controller when creating the payment
        self.validate_payment_logic(payment_data)
        self.define_card_brand(payment_data)

        # Create another validate payment logic but this time taking CardPaymentResponse so it checks if the card is still valid

        return self.checking_payment_is_successful(payment_data)
    
    def checking_payment_is_successful(self, payment: CardPaymentCreate) -> bool: # Maybe put this as CardPaymentResponse
        # Add more restrictions for a card payment to be denied
        if(payment.card_brand in [CardPaymentBrand.MASTER_CARD, CardPaymentBrand.VISA]):
            # FOR NOW, accept all card payments that have a brand
            return True
        else:
            # FOR NOW, decline all card that do not have a brand
            return False

    def define_card_brand(self, payment_data: CardPaymentCreate):
        card_digits = payment_data.card_digits.strip()

        # Defining card brand based on first digit
        if(card_digits[0] == "4"):
            payment_data.card_brand = CardPaymentBrand.VISA
        elif(card_digits[0] == "5"):
            payment_data.card_brand = CardPaymentBrand.MASTER_CARD
        else:
            payment_data.card_brand = CardPaymentBrand.NO_BRAND

    def validate_payment_logic(self, payment_data: CardPaymentCreate):
        card_digits = payment_data.card_digits.strip()

        # Calling helper functions for validation logic
        valid_digits = self.validate_card_digits(card_digits)
        valid_CVV = self.validate_card_CVV(payment_data.CVV)
        valid_expiration_date = self.validate_card_expiration_date(payment_data.expiration_month, payment_data.expiration_year)

        if(not valid_digits):
            raise ValueError(f"Invalid input: {card_digits}")
        elif(not valid_CVV):
            raise ValueError(f"Invalid input: {payment_data.CVV}")
        elif(not valid_expiration_date):
            raise ValueError(f"Invalid input: {payment_data.expiration_month}/{payment_data.expiration_year}")
    
    def validate_card_digits(self, digits: str) -> bool:
        isValid_flag = False

        # Ensuring card digits are in the appropriate format
        if(len(digits) == 16 and digits.isdigit()):
           isValid_flag = True

        return isValid_flag  
    
    def validate_card_expiration_date(self, expiration_month: int, expiration_year: int) -> bool:
        current_year = datetime.now().year
        current_month = datetime.now().month
        isExpirationValid_flag = False

        # Ensuring expiration date is valid
        if(expiration_month > 0 and expiration_month <= 12):
            if(expiration_year == current_year):
                if(expiration_month >= current_month):
                    isExpirationValid_flag = True
            elif(expiration_year > current_year):
                isExpirationValid_flag = True
        
        return isExpirationValid_flag
    
    def validate_card_CVV(self, digits: str) -> bool:
        isValid_flag = False

        # Ensuring CVV only has 3 digits
        if(len(digits) == 3 and digits.isdigit()):
           isValid_flag = True

        return isValid_flag  
    