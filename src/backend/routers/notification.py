from fastapi import APIRouter, Depends, HTTPException
from src.backend.controllers.notif_controller import NotificationController
from src.backend.models.notif import Notification, NotificationCreate
from typing import List

router = APIRouter(
    prefix="/notif",
    tags=["notif"]
)

def get_controller():
    return NotificationController()

@router.post("/", response_model=Notification)
def create_notif(notification: NotificationCreate, controller: NotificationController = Depends(get_controller)):
    new_notif = controller.create_notif(notification)
    return new_notif

@router.get("/{user_id}", response_model=List[Notification])
def get_notifs_by_user_id(user_id: int, controller: NotificationController = Depends(get_controller)):
    return controller.get_notifs_by_user_id(user_id)

@router.get("/{user_id}/unread", response_model=List[Notification])
def get_unread_notifs_by_user_id(user_id: int, controller: NotificationController = Depends(get_controller)):
    return controller.get_unread_notifs_by_user_id(user_id)

@router.put("/{notif_id}/read", response_model=Notification)
def mark_as_read(notif_id: int, controller: NotificationController = Depends(get_controller)):
    return controller.mark_as_read(notif_id)

@router.put("/{user_id}/read-all", response_model=List[Notification])
def mark_all_as_read_by_user_id(user_id: int, controller: NotificationController = Depends(get_controller)):
    return controller.mark_all_as_read_for_user(user_id)

@router.get("/{user_id}/unread-count", response_model=int)
def count_unread_notifications(user_id: int, controller: NotificationController = Depends(get_controller)):
    return controller.count_unread_notifs(user_id)

@router.delete("/{notif_id}", response_model=Notification)
def delete_notification(notif_id: int, controller: NotificationController = Depends(get_controller)):
    return controller.delete_notification(notif_id)

