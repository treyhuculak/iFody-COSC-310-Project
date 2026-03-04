from typing import Union
import json

class UserRepository:
    USER_FILE = 'data/user_db.json'
    
    def __init__(self) -> None:
        """
        Checks if data/user_db.json exists. If not, creates it and writes an empty JSON object.
        """
        try:
            with open(self.USER_FILE, "r") as file:
                users = json.load(file)["Users"]
                if users:
                    self.current_id = max([user["id"] for user in users]) + 1
                else:
                    self.current_id = 1
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.USER_FILE, "w") as file:
                json.dump({"Users": []}, file, indent = 4)
                # Because there are no instances in the database, we reset the current_id variable to 1.
                self.current_id = 1

    def add_user(self, user: dict[str, Union[str, int, bool]]) -> dict:
        '''
        Acts as the SaveUser functionality for adding Admin/Customer/RestaurantOwner instances to the database.
        '''
        with open(self.USER_FILE, "r") as file:
            users = json.load(file)["Users"]
            user["id"] = self.current_id
            self.current_id += 1
            users.append(user)
        with open(self.USER_FILE, "w") as file:
            json.dump({"Users": users}, file, indent = 4)
    
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
            
    def _reinit_database(self) -> None:
        """
        Removes all the Admin/Customer/RestaurantOwner instances from the database file.
        The function can only be used from user_repo_test.py and auth_controller_test.py for testing purposes.
        """
        with open(self.USER_FILE, "w") as file:
            json.dump({"Users": []}, file, indent = 4)
            self.current_id = 1