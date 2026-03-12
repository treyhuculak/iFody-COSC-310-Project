import json
from typing import Optional
from fastapi import HTTPException

class TransactionRepository:
    TRANSACTION_FILE = 'data/transaction.json'

    def __init__(self, file_path: Optional[str] = None) -> None:
        # check if files exist, if not create them with headers
        self.file_path = file_path or self.TRANSACTION_FILE
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # file doesn't exist or is corrupted, create/reset it with an empty list
            with open(self.file_path, 'w') as f:
                json.dump([], f, indent=4)
        pass

    def create_transaction(self, transaction_data: dict) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

            # Creating new transaction id based on last transaction added to transaction_data
            new_id = max([payment['id'] for payment in data], default=0) + 1
            transaction_data['id'] = new_id

            data.append(transaction_data)

            with open(self.file_path, 'w') as f:
                json.dump([transaction_data], f, indent=4)
            return transaction_data
        
        except FileNotFoundError:
            # Create a new file and store the transaction data
            transaction_data['id'] = 1
            with open(self.file_path, 'w') as f:
                json.dump([transaction_data], f, indent=4)
            return transaction_data
        
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Transaction missing id field: {e}")