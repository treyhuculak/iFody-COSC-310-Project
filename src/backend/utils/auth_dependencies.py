from fastapi import Header, HTTPException
from src.backend.models.user import Role
from src.backend.repositories.user_repo import UserRepository
 
# Initialize the UserRepository instance to be used
repo = UserRepository() 

def get_current_user(x_user_id: int = Header(...)):
    user_info = repo.get_user_by_id(x_user_id)
    if user_info is None: # If no such user
        raise HTTPException(status_code=401, detail="Invalid user ID")
    return user_info


def requires_role(*allowed_roles):
    def checker(x_user_id: int = Header(...)):
        user_info = repo.get_user_by_id(x_user_id)
        if user_info is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        try:
            user_role = Role(user_info['role'].lower())
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid role stored for user")
        
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied for this role")
        
        user_info["role"] = user_role
        return user_info
    
    return checker
