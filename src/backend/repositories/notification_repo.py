import json
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import HTTPException
from src.backend.models.notification import NotificationCreate

class NotificationRepository:
    NOTIFICATION_FILE = 'data/notification.json'

    def __init__(self, file_path: Optional[str] = None) -> None:
        # check if files exist, if not create them with headers
        self.file_path = file_path or self.NOTIFICATION_FILE
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except(FileNotFoundError, json.JSONDecodeError):
        # file doesn't exist or is corrupted, create/reset it with an empty list
            with open(self.file_path, 'w') as f:
                json.dump([], f, indent=4)

    def create_notification(self, notif_data: NotificationCreate) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

                notif_dict = notif_data.model_dump(mode= 'json')

                new_id = max([notif['id'] for notif in data], default=0) + 1
                notif_dict['id'] = new_id
                notif_dict['created_at'] = datetime.now().isoformat()

                data.append(notif_dict)
            
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
                return notif_dict
        except FileNotFoundError:
            notif_dict = notif_data.model_dump(mode= 'json')
            notif_dict['id'] = 1
            notif_dict['created_at'] = datetime.now().isoformat()
            with open(self.file_path, 'w') as f:
                json.dump([notif_dict], f, indent=4)
            return notif_dict
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Notification missing id field: {e}")
    
    def get_notifications_by_user_id(self, user_id: int) -> List[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                user_notifs = [notif for notif in data if notif.get("user_id") == user_id]
                return user_notifs

        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail=f"File {self.file_path} not found")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        
    
    def get_unread_notifications_by_user_id(self, user_id: int) -> List[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                unread_notifs = [notif for notif in data if notif.get("user_id") == user_id and notif.get("is_read") == False]
                return unread_notifs
        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail=f"File {self.file_path} not found")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        
    
    def mark_as_read(self, notification_id: int) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                notif = next((notif for notif in data if notif.get("id") == notification_id), None)
                if notif:
                    notif["is_read"] = True
                else:
                    raise HTTPException(status_code=404, detail="Notification not found")
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return notif
        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail=f"File {self.file_path} not found")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
    
    def mark_all_as_read_for_user(self, user_id: int) -> List[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                notifs = [notif for notif in data if notif.get("user_id") == user_id and notif.get("is_read") == False]
                for notif in notifs:
                    notif["is_read"] = True
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return notifs
        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail=f"File {self.file_path} not found")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")

    def delete_notification(self, notif_id: int) -> dict:
        try:
            with open (self.file_path, 'r') as f:
                data = json.load(f)
            deleted_notif = None
            for k, notif in enumerate(data):
                if notif.get("id") == notif_id:
                    deleted_notif = data.pop(k)
                    break
            if deleted_notif is None:
                raise HTTPException(status_code=404, detail = "Notification not found")
            with open (self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return deleted_notif
        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail=f"File {self.file_path} not found")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        
    def count_unread(self, user_id: int) -> int:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                notifs = [notif for notif in data if notif.get("user_id") == user_id and notif.get("is_read") == False]
            return len(notifs)
        
        except FileNotFoundError:
            raise HTTPException(status_code = 404, detail=f"File {self.file_path} not found")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")


