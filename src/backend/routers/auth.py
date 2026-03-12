from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.backend.controllers.auth_controller import AuthController, AccountExistsException
from src.backend.models.user import Role

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_controller():
    return AuthController()

# Define the expected JSON payload structure for register and login endpoints
# Pydantic validation will automatically check the types for these fields
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Role

class LoginRequest(BaseModel):
    email: str
    password: str

# Receives data through RegisterRequest and LoginRequest and calls auth_controller's register method
# Return a simple message after success
@router.post("/register")
def register_user(data: RegisterRequest, controller: AuthController = Depends(get_controller)):
    
    try:
        controller.register(
        username = data.username,
        email = data.email,
        password = data.password,
        role = data.role
        )
        return {"message": "Account created successfully."}
    except AccountExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))

# Receives data through LoginRequest and calls auth_controller's login method
# Return a simple message after success, along with the user's email and role
@router.post("/login")
def login_user(data: LoginRequest, controller: AuthController = Depends(get_controller)):
    user = controller.login(data.email, data.password)
    return {
        "message" : "Login successful.",
        "username" : user["id"],
        "email" : user["email"],
        "role" : user["role"]
    }

