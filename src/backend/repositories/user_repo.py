import json

class UserRepository:
    USER_FILE = 'data/user_db.json'
    
    def __init__(self):
        '''
        Checks if data/user_db.json exists. If not, creates it and writes the headers.
        '''
        self.user_db_location = self.USER_FILE
        try:
            with open(self.user_db_location, "r") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.user_db_location, "r") as file:
                json.dump([], file, indent = 4)
    
    def get_all_users(self):
        '''
        Returns all the Admin/Customer/RestaurantOwner instances from the database.
        '''
        with open(self.user_db_location) as file:
            users = json.load(file)['Users']
            return users
    
    def get_user_by_id(self, id: int):
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the id.
        '''
        with open(self.user_db_location) as file:
            users = json.load(file)['Users']
            for user in users:
                if user['id'] == id:
                    return user
            else:
                return None
    
    def get_user_by_username(self, username: str):
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the username.
        '''
        with open(self.user_db_location) as file:
            users = json.load(file)['Users']
            for user in users:
                if user['username'] == username :
                    return user
            else:
                return None

    
    def get_user_by_email(self, email: str):
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the email.
        '''
        with open(self.user_db_location) as file:
            users = json.load(file)['Users'] 
            for user in users:
                if user['email'] == email :
                    return user
            else:
                return None