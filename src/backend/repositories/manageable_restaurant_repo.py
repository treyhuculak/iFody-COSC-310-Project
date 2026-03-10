from src.backend.repositories import user_repo, restaurant_repo

class ManageableRestaurantRepository:
    def __init__(
            self,
            user_repo_file: str = None,
            rest_repo_file: str = None
        ) -> None:
        '''
        Initializes a ManageableRestaurantRepository instance using the user_repo_file and rest_repo_file arguments.
        '''
        pass