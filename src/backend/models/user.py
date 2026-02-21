import re

class _User:
    '''
    This is the base class for the Customer, RestaurantOwner, and Admin classes.
    This class is not intended for direct instantiation of _User objects.
    '''
    def __init__(
            self,
            username: str,
            emailaddress: str,
            password: str,
            role: str,
            is_blocked: bool
    ) -> None:
        '''
        Constructs a _User instance with the given arguments.
        '''
        # All the attributes should be private to prevent them from being modified outside the class.
        self.__username = username
        self.__emailaddress = emailaddress
        self.__password = password
        self.__role = role
        self.__is_blocked = is_blocked

    def __repr__(self) -> str:
        '''
        Returns a demonstration string for debugging purposes.
        '''
        return "_User(%r, %r, %r, %r, %r)" % (
            self.__username,
            self.__emailaddress,
            self.__password,
            self.__role,
            self.__is_blocked
        )
    
    def get_username(self) -> str:
        '''
        Returns the value of the username attribute.
        '''
        return self.__username
    
    def get_emailaddress(self) -> str:
        '''
        Returns the value of the emailaddress attribute.
        '''
        return self.__emailaddress
    
    def get_password(self) -> str:
        '''
        Returns the value of the password attribute.
        '''
        return self.__password
    
    def get_role(self) -> str:
        '''
        Returns the value of the role attribute.
        '''
        return self.__role
    
    def get_is_blocked(self) -> str:
        '''
        Returns the value of the is_blocked attribute.
        '''
        return self.__is_blocked
    
    def _set_is_blocked(self, status: bool) -> None:
        '''
        Sets the user's status to blocked (True) or unblocked (False).
        The function is hidden as we assume only admin accounts can use it.
        '''
        self.__is_blocked = status

    def login(self) -> None:
        '''
        This function enables different types of accounts to log in.
        This draft assumes that each account type maintains its own database, the details of which are not included here.
        '''
        email_pattern = re.fullmatch(
            "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
            self.__emailaddress
        )

        if (email_pattern is None):
            raise ValueError("The email address is invalid.")
        
        password_pattern = re.fullmatch(
            "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$#%])[A-Za-z\\d@$#%]{8,10}$",
            self.__password
        )

        if (password_pattern is None):
            raise ValueError("The password must contain at least one number, one uppercase letter, one lowercase letter, one special character, and be between 8 and 10 characters long.")
        
    def logout(self) -> None:
        '''
        The logout function is also a prototype in the _User class intended to be overridden.
        '''
        pass

class Customer(_User):
    def __init__(
            self,
            username: str,
            emailaddress: str,
            password: str,
            is_blocked: bool
    ) -> None:
        '''
        Constructs a Customer instance with the given arguments.
        '''
        super().__init__(
            username, emailaddress, password, "customer", False
        )

    def __repr__(self) -> str:
        '''
        Returns a demonstration string for debugging purposes.
        '''
        return "Customer" + super().__repr__()[5:]
    
    def review_order_history(self) -> str:
        '''
        Implements the functionality that enables Customer instances to view their orders.
        This is also left as a prototype function at the moment.
        '''
        pass