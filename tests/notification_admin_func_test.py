import pytest
import json
from fastapi.testclient import TestClient
from src.backend.controllers.auth_controller import AuthController
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.controllers.notification_controller import NotificationController
from src.backend.models.notification import NotificationType
from src.backend.models.user import Role

@pytest.fixture



test_auth_controller = AuthController(
        repo=test_user_repo,
        notif_controller=test_notif_controller
    )


def test_block_user_notification(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_auth_controller = test_client
    client.post(
        "/auth/login/",
        json = {
            "email": "testadmin@123.com",
            "password": "Test@123"
        }
    )
    client.post("/auth/blocked/%s" % "TestCustomer")

    notifications = json.loads(temp_notif_db.read_text())
    assert notifications[0] ["user_id"] == 1
    assert notifications[0] ["type"] == NotificationType.BLOCKED_ACCOUNT.value
    assert notifications[0] ["is_read"] == False
    assert notifications[0] ["message"] == "Your account has been blocked by the administrator"