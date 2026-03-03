from pydantic import BaseModel, Field, field_validator
import re

email_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$#%])[A-Za-z\\d@$#%]{8,10}$"
role_pattern = "^(Admin|Customer|RestaurantOwner)$"

class UserBase(BaseModel):
    id: int = Field(..., ge = 1)
    username: str = Field(..., min_length = 1)
    email: str = Field(..., pattern = email_pattern)
    password: str = Field(..., min_length = 1)
    role: str = Field(..., pattern = role_pattern)
    is_logged_in: bool = False
    is_blocked: bool = False

    @field_validator('password')
    def check_password(cls, password_input: str) -> str:
        result = re.fullmatch(
            password_pattern,
            password_input
        )

        if result:
            return result
        else:
            raise ValueError('The password must contain at least one number, one uppercase letter, one lowercase letter, one special character, and be between 8 and 10 characters long.')

class Admin(UserBase):
    role: str = 'Admin'
    is_logged_in: bool = True

class Customer(UserBase):
    role: str = 'Customer'
    is_logged_in: bool = True

class RestaurantOwner(UserBase):
    role: str = 'RestaurantOwner'
    is_logged_in: bool = True