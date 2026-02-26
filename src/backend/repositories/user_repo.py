import json

class UserRepository():
    CUSTOMER_FILE = 'data/customer_db.json'
    
    def __init__(self):
        # check if files exist, if not create them with headers
        pass
    
    def getAllUsers(self):
        with open(self.CUSTOMER_FILE) as file:
            users = json.load(file)['users']
            return users
    
    def getUserByID(self): #not necessary for now
        return []
    
    def getUserByUsername(self, username): #return the user's Username
        with open(self.CUSTOMER_FILE) as file:
            users = json.load(file)['users']
            for row in users:
                if row['username'] == username :
                    return row
            return None

    
    def getUserByEmail(self, email):
        with open(self.CUSTOMER_FILE) as file:
            users = json.load(file)['users'] 
            for row in users:
                if row['email'] == email :
                    return row
            return None
    
    def getUserByRole(self):
        return []
    
