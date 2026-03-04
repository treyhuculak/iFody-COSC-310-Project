import json

class UserRepository:
    USER_FILE = 'data/user_db.json'
    
    def __init__(self) -> None:
        """
        Checks if data/user_db.json exists. If not, creates it and writes an empty JSON object.
        """
        try:
            with open(self.USER_FILE, "r") as handle:
                json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.USER_FILE, "w") as handle:
                json.dump([], handle, indent = 4)
    
    def get_all_users(self) -> list[dict]:
        '''
        Returns all the Admin/Customer/RestaurantOwner instances from the database.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users']
            return users
    
    def get_user_by_id(self, id: int) -> dict:
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the id.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users']
            for user in users:
                if user['id'] == id:
                    return user
            else:
                return None
    
    def get_user_by_username(self, username: str) -> dict:
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the username.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users']
            for user in users:
                if user['username'] == username:
                    return user
            else:
                return None
    
    def get_user_by_email(self, email: str) -> dict:
        '''
        Returns the Admin/Customer/RestaurantOwner instance according to the email.
        '''
        with open(self.USER_FILE) as file:
            users = json.load(file)['Users']
            for user in users:
                if user['email'] == email:
                    return user
            else:
                return None