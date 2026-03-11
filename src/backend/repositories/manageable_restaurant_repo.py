import json
from src.backend.repositories import user_repo, restaurant_repo

class NotARestaurantOwnerError(Exception):
    '''
    Raise it when the retrieved account is not a RestaurantOwner instance.
    '''
    pass

class RestaurantLinkedException(Exception):
    '''
    Raise it when the Restaurant is already associated with a RestaurantOwner instance.
    '''
    pass

class ManageableRestaurantRepository:
    def __init__(
            self,
            user_repo_file: str = None,
            rest_repo_file: str = None,
            manageable_rests: str = None
        ) -> None:
        '''
        Initializes a ManageableRestaurantRepository instance with the user_repo_file, rest_repo_file, and manageable_rests arguments.
        '''
        # We check whether alternative file paths are given, otherwise, we use the default paths.
        # The field self.manageable_rests_file is a database that shows which restaurant owners manage which restaurants.
        user_repo_file = user_repo_file or "data/user_db.json"
        rest_repo_file = rest_repo_file or "data/restaurants.json"
        self.manageable_rests_file = manageable_rests or "data/manageable_rests.json"

        # We call the initializers for UserRepository and RestaurantRepository.
        self.user_repo = user_repo.UserRepository(user_repo_file)
        self.rest_repo = restaurant_repo.RestaurantRepository(rest_repo_file)

        try:
            with open(self.manageable_rests_file, "r") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.manageable_rests_file, "w") as file:
                json.dump({}, file, indent = 4)

    def add_restaurant_to_restaurant_owner(self, restaurant_owner_id: int, restaurant_id: int) -> None:
        retrieved_user = self.user_repo.get_user_by_id(restaurant_owner_id)
        if (not retrieved_user) or (retrieved_user["role"] != "restaurant owner"):
            raise NotARestaurantOwnerError("This is not a RestaurantOwner account.")
        else:
            retrieved_restaurant = self.rest_repo.get_restaurant_by_id(restaurant_id)
            if (not retrieved_restaurant) or retrieved_restaurant["is_linked"]:
                raise RestaurantLinkedException("This Restaurant instance is already associated with a RestaurantOwner.")
            else:
                try:
                    with open(self.manageable_rests_file, "r") as file:
                        rest_owner_accounts = json.load(file)
                        if rest_owner_accounts:
                            for id_number in rest_owner_accounts:
                                if id_number == restaurant_owner_id:
                                    if restaurant_id not in rest_owner_accounts[restaurant_owner_id]:
                                        rest_owner_accounts[restaurant_owner_id].append(restaurant_id)
                            json.dump(rest_owner_accounts, file, indent = 4)
                        else:
                            raise RuntimeError("The variable rest_owner_accounts contains nothing, letting the except block handle it...")
                except (RuntimeError, FileNotFoundError, json.JSONDecodeError):
                    retrieved_restaurant["is_linked"] = True
                    self.rest_repo.update_restaurant(restaurant_id, retrieved_restaurant)
                    new_restowner_rest_pair = dict()
                    new_restowner_rest_pair[restaurant_owner_id] = [restaurant_id]
                    with open(self.manageable_rests_file, "w") as file:
                        json.dump(new_restowner_rest_pair, file, indent = 4)