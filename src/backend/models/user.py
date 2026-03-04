from pydantic import BaseModel, Field, field_validator
import re

email_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$#%])[A-Za-z\\d@$#%]{8,10}$"
role_pattern = "^(Admin|Customer|RestaurantOwner)$"

class InvalidEmailError(Exception):
    pass

class InvalidPasswordError(Exception):
    pass

class InvalidRoleError(Exception):
    pass

class UserBase(BaseModel):
    id: int = Field(..., ge = 1)
    username: str = Field(..., min_length = 1)
    email: str = Field(..., min_length = 1)
    password: str = Field(..., min_length = 1)
    role: str = Field(..., min_length = 5)
    is_logged_in: bool = False
    is_blocked: bool = False

    @field_validator('email')
    def check_email(cls, email_input: str) -> str:
        result = re.fullmatch(
            email_pattern,
            email_input
        )

        if result:
            return result
        else:
            raise InvalidEmailError('The email address is in an invalid format.')

    @field_validator('password')
    def check_password(cls, password_input: str) -> str:
        result = re.fullmatch(
            password_pattern,
            password_input
        )

        if result:
            return result
        else:
            raise InvalidPasswordError('The password must contain at least one number, one uppercase letter, one lowercase letter, one special character, and be between 8 and 10 characters long.')
        
    @field_validator('role')
    def check_role(cls, role_input: str) -> str:
        result = re.fullmatch(
            role_pattern,
            role_input
        )

        if result:
            return result
        else:
            raise InvalidRoleError('The role must be one of: Admin, Customer, or RestaurantOwner.')

class Admin(UserBase):
    role: str = 'Admin'
    is_logged_in: bool = True

class Customer(UserBase):
    role: str = 'Customer'
    is_logged_in: bool = True

class RestaurantOwner(UserBase):
    role: str = 'RestaurantOwner'
    is_logged_in: bool = True