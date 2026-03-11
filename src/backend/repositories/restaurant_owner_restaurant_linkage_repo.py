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

class RestaurantOwnerRestaurantLinkageRepo:
    def __init__(
            self,
            user_repo_file: str = None,
            rest_repo_file: str = None,
            manageable_rests: str = None
        ) -> None:
        '''
        Initializes a RestaurantOwnerRestaurantLinkageRepo instance with the user_repo_file, rest_repo_file, and manageable_rests arguments.
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

    def add_restaurant_to_restaurant_owner(self, restaurant_id: int, restaurant_owner_id: int) -> None:
        '''
        Associates a Restaurant instance with a valid RestaurantOwner instance.
        '''
        retrieved_user = self.user_repo.get_user_by_id(restaurant_owner_id)
        if (not retrieved_user) or ("owner" not in retrieved_user["role"].lower()):
            raise NotARestaurantOwnerError("This is not a RestaurantOwner account.")
        else:
            retrieved_restaurant = self.rest_repo.get_restaurant_by_id(restaurant_id)
            if (not retrieved_restaurant) or retrieved_restaurant["is_linked"]:
                raise RestaurantLinkedException("This Restaurant instance is already associated with a RestaurantOwner.")
            else:
                try:
                    retrieved_restaurant["owner_id"] = restaurant_owner_id
                    retrieved_restaurant["is_linked"] = True
                    self.rest_repo.update_restaurant(restaurant_id, retrieved_restaurant)
                    with open(self.manageable_rests_file, "r") as file:
                        rest_owner_accounts = json.load(file)
                        if rest_owner_accounts:
                            for id_number in rest_owner_accounts:
                                if int(id_number) == restaurant_owner_id:
                                    # The json module converts nonstring keys into strings, so we need to ensure the value is returned correctly when it is read back.
                                    restaurant_owner_id = str(restaurant_owner_id)
                                    if restaurant_id not in rest_owner_accounts[restaurant_owner_id]:
                                        rest_owner_accounts[restaurant_owner_id].append(restaurant_id)
                            with open(self.manageable_rests_file, "w") as file:
                                json.dump(rest_owner_accounts, file, indent = 4)
                        else:
                            raise RuntimeError("The variable rest_owner_accounts contains nothing, letting the except block handle it...")
                except (RuntimeError, FileNotFoundError, json.JSONDecodeError):
                    new_restowner_rest_pair = dict()
                    new_restowner_rest_pair[restaurant_owner_id] = [restaurant_id]
                    with open(self.manageable_rests_file, "w") as file:
                        json.dump(new_restowner_rest_pair, file, indent = 4)

    def get_restaurants_by_restaurant_owner_id(self, restaurant_owner_id: int) -> list[dict]:
        '''
        Retrieves all the Restaurant instances as a list based on the ID of the RestaurantOwner instance.
        '''
        retrieved_user = self.user_repo.get_user_by_id(restaurant_owner_id)
        if (not retrieved_user) or ("owner" not in retrieved_user["role"].lower()):
            raise NotARestaurantOwnerError("This is not a RestaurantOwner account.")
        else:
            try:
                with open(self.manageable_rests_file, "r") as file:
                    # Although we use an integer as the key, the json module still stores it as a string.
                    restaurants = json.load(file)[str(restaurant_owner_id)]
                    restaurants = [self.rest_repo.get_restaurant_by_id(rest_id) for rest_id in restaurants]
                    print(restaurants)
                    return restaurants
            except KeyError:
                return []
