from src.backend.services.admin_service import AdminService

class AdminServiceController:
    def __init__(
            self,
            admin_service: AdminService = None
        ):
        self.service = admin_service or AdminService()

    def format_all_orders(self) -> str:
        pass

    def format_most_popular_restaurant(self) -> str:
        pass