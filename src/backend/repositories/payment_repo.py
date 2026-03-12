import json
from typing import Optional
from fastapi import HTTPException
from src.backend.models.payment import PaymentOptions

class PaymentRepository:
    PAYMENT_FILE = 'data/payment.json'

    def __init__(self, file_path: Optional[str] = None) -> None:
        # check if files exist, if not create them with headers
        self.file_path = file_path or self.PAYMENT_FILE
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # file doesn't exist or is corrupted, create/reset it with an empty list
            with open(self.file_path, 'w') as f:
                json.dump([], f, indent=4)
        pass

    def get_payment_by_id(self, payment_id: int) -> Optional[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Getting the first payment that matches the provided payment_id 
                payment = next(filter(lambda p: p.get("id") == payment_id, data), None)
                return payment
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Payment missing id field: {e}")

    def create_payment_method(self, payment_data: dict) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

                # Creating new payment id based on last payment added to payment_data
                new_id = max([payment['id'] for payment in data], default=0) + 1
                payment_data['id'] = new_id

                if(payment_data["method"] == PaymentOptions.CASH.value):
                    # FOR NOW, accept all cash payments
                    payment_data['is_successful'] = True
                else:
                    # Only retain 4 last digits for best practises
                    payment_data['last4'] = "".join([payment_data['card_digits'][-4], payment_data['card_digits'][-3], payment_data['card_digits'][-2], payment_data['card_digits'][-1]])
                    
                    # Removing critical user information (best practise)
                    del payment_data['card_digits']
                    del payment_data['CVV']

                data.append(payment_data)
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return payment_data
        
        except FileNotFoundError:
            # create a new file and store the payment data
            payment_data['id'] = 1
            if(payment_data["method"] == PaymentOptions.CASH.value):
                # FOR NOW, accept all cash payments
                payment_data['is_successful'] = True
            else:
                payment_data['last4'] = "".join([payment_data['card_digits'][-4], payment_data['card_digits'][-3], payment_data['card_digits'][-2], payment_data['card_digits'][-1]])
                    
                # Removing critical user information (best practise)
                del payment_data['card_digits']
                del payment_data['CVV']

            with open(self.file_path, 'w') as f:
                json.dump([payment_data], f, indent=4)
            return payment_data
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Payment missing id field: {e}")
        
    def delete_payment_method(self, payment_id: int) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                new_data = data.copy()
                deleted_payment = None
                
                # Iterating data to find the payment key and then deleting it from new_data
                for k, pay in enumerate(data):
                    if pay["id"] == payment_id:
                        deleted_payment = new_data.pop(k)
                        break
                
                # If nothing is found
                if deleted_payment == None:
                    raise HTTPException(status_code=404, detail=f"Payment with id {payment_id} not found.")
                
                # Saving changes
                with open(self.file_path, 'w') as f:
                    json.dump(new_data, f, indent=4)

                return deleted_payment
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Payment missing id field: {e}")