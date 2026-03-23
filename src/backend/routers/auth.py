from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi import HTTPException
from src.backend.controllers.auth_controller import AuthController, AccountExistsException
from src.backend.models.user import Role

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_controller():
    return AuthController()

'''
Defines the expected JSON payload structure for the register and login endpoints.
Pydantic validation automatically enforces the field types.
'''
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Role

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register_user(data: RegisterRequest, controller: AuthController = Depends(get_controller)):
    '''
    Receives data through RegisterRequest and LoginRequest and calls the auth_controller's register method.
    Returns a simple success message.
    '''
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

@router.post("/login")
def login_user(data: LoginRequest, controller: AuthController = Depends(get_controller)):
    '''
    Receives data through LoginRequest and calls the auth_controller's login method.
    Returns a simple success message along with the user's email and role.
    '''
    user = controller.login(data.email, data.password)
    return {
        "message": "Logged in successfully.",
        "username": user["id"],
        "email": user["email"],
        "role": user["role"]
    }

@router.post("/blocked/{username}")
def block_user(username: str, controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the block_user method.
    Blocks the user account according to the username.
    '''
    blocked = controller.block_user(username)
    return blocked

@router.delete("/blocked/{username}")
def unblock_user(username: str, controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the unblock_user method.
    Unblocks the user account according to the username.
    '''
    unblocked = controller.unblock_user(username)
    return unblocked

@router.delete("/register/{username}")
def delete_user(username: str, controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the delete_user method.
    Deletes the user account according to the username.
    '''
    deleted = controller.delete_user(username)
    return deleted

@router.get("/statistics/order")
def get_all_orders(controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the get_all_orders method.
    Gets all the orders when requested by an administrator.
    '''
    return controller.get_all_orders()

@router.get("/statistics/gross_revenue/{restaurant_id}")
def get_gross_revenue_by_restaurant_id(restaurant_id: int, controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the get_gross_revenue_by_restaurant_id method.
    Gets the gross revenue of a restaurant based on the given restaurant_id value.
    '''
    return controller.get_gross_revenue_by_restaurant_id(restaurant_id)

@router.get("/statistics/average_delivery_time")
def get_average_delivery_time(controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the get_average_delivery_time method.
    Gets the average delivery time for all the restaurant orders.
    '''
    return controller.get_average_delivery_time()

@router.get("/statistics/most_popular_restaurant")
def get_most_popular_restaurant(controller: AuthController = Depends(get_controller)):
    '''
    A wrapper function for the get_most_popular_restaurant method.
    Gets the most popular restaurant based on the number of orders, using the lowest restaurant_id value.
    '''
    return controller.get_most_popular_restaurant()