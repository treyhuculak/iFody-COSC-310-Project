import re

class User:
    def __init__(
            self,
            username: str,
            emailaddress: str,
            password: str,
            role: str,
            is_blocked: bool
    ) -> None:
        '''
        Constructs a User instance with the given arguments.
        '''
        # All the attributes should be private to prevent them from being modified outside the class.
        self.__username = username

        emailpattern = re.fullmatch(
            "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
            emailaddress
        )
        if (emailpattern is None):
            raise ValueError("The email address is invalid.")
        self.__emailaddress = emailaddress

        self.__password = password
        self.__role = role
        self.__is_blocked = is_blocked

    def __repr__(self) -> str:
        '''
        Returns a demonstration string for debugging purposes.
        '''
        return "User(%r, %r, %r, %r, %r)" % (
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