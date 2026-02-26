import csv
from src.backend.models.user import Customer

class UserRepository():
    CUSTOMER_FILE = 'data/customer_db.csv'
    
    def __init__(self):
        # check if files exist, if not create them with headers
        pass
    
    def getAllUsers(self):
        return []
    
    def getUserByID(): #not necessary for now
        return []
    
    def getUserByUsername(self, username): #return the user's Username
        with open(self.CUSTOMER_FILE, newline="") as file:
            reader = csv.DictReader(file) 
            for row in reader:
                if (row['username'] == username) :
                    return row
            return None
                    
    
    def getUserByEmail(self, email):
        with open(self.CUSTOMER_FILE, newline="") as file:
            reader = csv.DictReader(file) 
            for row in reader:
                if (row['email'] == email) :
                    return row
            return None
    
    def getUserByRole():
        return []
    
