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

    def get_transaction_by_id(self, transaction_id: int) -> Optional[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Getting the first transaction that matches the provided transaction_id 
                transaction = next(filter(lambda t: t.get("id") == transaction_id, data), None)
                return transaction
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Transaction missing id field: {e}")
        
    def get_all_transactions_by_user_id(self, user_id: int) -> list[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Getting the list of transactions that have the same user_id 
                list_of_transactions = list(filter(lambda t: t['user_id'] == user_id, data))
                return list_of_transactions
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Transaction missing user id field: {e}")

    def create_transaction(self, transaction_data: dict) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

            # Creating new transaction id based on last transaction added to transaction_data
            new_id = max([payment['id'] for payment in data], default=0) + 1
            transaction_data['id'] = new_id

            data.append(transaction_data)

            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
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
        
    def delete_transaction(self, transaction_id: int) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                new_data = data.copy()
                deleted_transaction = None
                
                # Iterating data to find the transaction key and then deleting it from new_data
                for k, transaction in enumerate(data):
                    if transaction["id"] == transaction_id:
                        deleted_transaction = new_data.pop(k)
                        break
                
                # If nothing is found
                if deleted_transaction == None:
                    raise HTTPException(status_code=404, detail=f"Transaction with id {transaction_id} not found.")
                
                # Saving changes
                with open(self.file_path, 'w') as f:
                    json.dump(new_data, f, indent=4)

                return deleted_transaction
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Transaction missing id field: {e}")