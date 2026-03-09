from src.backend.models.notif import Notification, NotificationCreate
from src.backend.repositories.notif_repo import NotificationRepository
from fastapi import HTTPException
from typing import List

class NotificationController:
    def __init__(self) -> None:
        self.notif_repo = NotificationRepository()
    
    def get_notifs_by_user_id(self, user_id: int) -> List[dict]:
        return self.notif_repo.get_notifications_by_user_id(user_id)

    def create_notif(self, notif_data: NotificationCreate) -> dict:
        return self.notif_repo.create_notification(notif_data)
    
    def get_unread_notifs_by_user_id(self, user_id: int) -> List[dict]:
        return self.notif_repo.get_unread_notifications_by_user_id(user_id)
    
    def mark_as_read(self, notif_id: int) -> dict:
        return self.notif_repo.mark_as_read(notif_id)
    
    def mark_all_as_read_for_user(self, user_id: int) -> List[dict]:
        return self.notif_repo.mark_all_as_read_for_user(user_id)
    
    def count_unread_notifs(self, user_id: int) -> int:
        return self.notif_repo.count_unread(user_id)
    
    def delete_notification(self, notif_id: int) -> dict:
        return self.notif_repo.delete_notification(notif_id)
    