import json

class UserRepository:
    USER_FILE = 'data/user_db.json'
    
    def __init__(self):
        '''
        Checks if data/user_db.json exists. If not, creates it and writes the headers.
        '''
        pass
    
    def get_all_users(self):
        '''
        Returns all the Admin/Customer/RestaurantOwner instances from the database.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users']
            return users
    
    def get_user_by_id(self):
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the id.
        '''
        return []
    
    def get_user_by_username(self, username):
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the username.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users']
            for row in users:
                if row['username'] == username :
                    return row
            return None

    
    def get_user_by_email(self, email):
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the email.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users'] 
            for row in users:
                if row['email'] == email :
                    return row
            return None