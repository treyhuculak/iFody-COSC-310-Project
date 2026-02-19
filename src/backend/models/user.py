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

        emailpattern = re.search(
            "/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/",
            emailaddress
        )
        if (emailpattern is None):
            raise ValueError("The email address is invalid.")
        self.__emailaddress = emailaddress

        self.__password = password
        self.__role = role
        self.__is_blocked = is_blocked