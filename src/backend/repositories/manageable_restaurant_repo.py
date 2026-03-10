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
        # We check whether alternative file paths are given, otherwise, we use the default paths.
        user_repo_file = user_repo_file or "data/user_db.json"
        rest_repo_file = rest_repo_file or "data/restaurants.json"

        self.user_repo = user_repo.UserRepository(user_repo_file)
        self.rest_repo = restaurant_repo.RestaurantRepository(rest_repo_file)