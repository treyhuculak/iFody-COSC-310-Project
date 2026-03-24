from typing import Optional, Union

from fastapi import HTTPException
from src.backend.models.user import UserSave, Role
from src.backend.models.notification import NotificationType, NotificationCreate
from src.backend.controllers.notification_controller import NotificationController
from src.backend.repositories.user_repo import UserRepository
from src.backend.services.admin_service import AdminService

class AccountExistsException(Exception):
    """
    Raise it when the account is already in the database for the register function.
    """
    pass

class NotLoggedInException(Exception):
    '''
    Raise it when the user attempts to log out but no account is logged in.
    '''
    pass

class AuthController:
    def __init__(
            self,
            repo: Optional[UserRepository] = None,
            service: Optional[AdminService] = None,
            notif_controller: Optional[NotificationController] = None
        ) -> None:
        '''
        Initializes the AuthController class with the necessary fields.
        A self.cur_user variable is added to keep track of the potentially logged-in user account.
        '''
        self.cur_user = None
        self.repo = repo or UserRepository()
        self.service = service or AdminService()
        self.notif_controller = notif_controller or NotificationController()


    def register(self, username: str, email: str, password: str, role: Role):
        '''
        Creates an account instance and saves it to the database when the email, password, and role are all valid.
        '''
        users = self.repo.get_all_users()
        usernames = [user["username"] for user in users]
        emails = [user["email"] for user in users]
        if (username in usernames) or (email in emails):
            raise AccountExistsException("The account already exists. Try logging in to the account.")
        new_user = UserSave(id = 1, username = username, email = email, password = password, role = role)
        user_dict = new_user.model_dump()
        if hasattr(user_dict['role'], 'value'):
            user_dict['role'] = user_dict['role'].value
        self.repo.add_user(user_dict)
        
    def login(self, email: str, password: str):
        '''
        Logs in using the email and password given.
        '''
        user_info = self.repo.get_user_by_email(email)
        if user_info == None:
            raise HTTPException(status_code = 404, detail = "The account is not found.")
        if password == user_info['password']:
            user_info["is_logged_in"] = True
            self.cur_user = user_info
            return self.cur_user
        else:
            raise HTTPException(status_code = 400, detail = "The password is incorrect.")
        
    def logout(self) -> None:
        '''
        Logs out the user and updates the is_logged_in field in the dictionary.
        '''
        if self.cur_user:
            self.cur_user["is_logged_in"] = False
            self.cur_user = None
        else:
            raise NotLoggedInException("Please sign in to the account first.")
        
    def delete_user(self, username: str) -> Union[dict, None]:
        '''
        A wrapper function for delete_user that allows only administrators to delete a user by username.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                return self.service.delete_user(username)
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can delete accounts.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators can delete accounts.")
        
    def block_user(self, username: str) -> Union[dict, None]:
        '''
        A wrapper function for block_user that allows only administrators to block a user by username.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                blocked_notif = NotificationCreate(
                    user_id = self.cur_user["id"],
                    type = NotificationType.BLOCKED_ACCOUNT,
                    title = "Account has been blocked",
                    message = "Your account has been blocked by the administrator",
                    is_read = False,
                )
                self.notif_controller.create_notif(blocked_notif)
                return self.service.block_user(username)
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can block accounts.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators can block accounts.")
        
    def unblock_user(self, username: str) -> Union[dict, None]:
        '''
        A wrapper function for unblock_user that allows only administrators to unblock a user by username.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                user_id = self.cur_user["id"]
                unblocked_notif = NotificationCreate(
                    user_id = user_id,
                    type = NotificationType.UNLBOCKED_ACCOUNT,
                    title = "Account has been unblocked",
                    message = f"Your account has been unblocked by the administrator",
                    is_read = False,
                )
                self.notif_controller.create_notif(unblocked_notif)
                return self.service.unblock_user(username)
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can unblock accounts.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators can unblock accounts.")

    def get_all_orders(self) -> list[dict]:
        '''
        A wrapper function for get_all_orders that allows only administrators to access all the orders.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                return self.service.get_all_orders()
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can access all the orders.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators can access all the orders.")
        
    def get_gross_revenue_by_restaurant_id(self, restaurant_id: int) -> float:
        '''
        A wrapper function for get_gross_revenue_by_restaurant_id that allows only administrators to check the gross revenue of the restaurant.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                return self.service.get_gross_revenue_by_restaurant_id(restaurant_id)
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can check the gross revenue of the restaurant.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators owners can check the gross revenue of the restaurant.")
        
    def get_average_delivery_time(self) -> float:
        '''
        A wrapper function for get_average_delivery_time that allows only administrators to check the average delivery time.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                return self.service.get_average_delivery_time()
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can check the average delivery time.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators can check the average delivery time.")
        
    def get_most_popular_restaurant(self) -> Union[dict, None]:
        '''
        A wrapper function for get_most_popular_restaurant that allows only administrators to check the most popular restaurant.
        '''
        if self.cur_user:
            if self.cur_user["role"] == Role.ADMIN.value:
                return self.service.get_most_popular_restaurant()
            else:
                raise HTTPException(status_code = 403, detail = "Only administrators can check the most popular restaurant.")
        else:
            raise HTTPException(status_code = 401, detail = "Only logged-in administrators can check the most popular restaurant.")