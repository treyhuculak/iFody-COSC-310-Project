import pytest, json
from fastapi.testclient import TestClient
from src.backend.models.notification import NotificationType
from src.backend.models.user import Role
from src.backend.controllers.notification_controller import NotificationController
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.controllers.auth_controller import AuthController
from src.backend.repositories.user_repo import UserRepository
from src.backend.services.admin_service import AdminService
import src.backend.utils.auth_dependencies as auth_dependencies
from src.backend.routers.auth import get_controller
from src.backend.main import app

@pytest.fixture
def test_client(tmp_path):
    temp_notif_db = tmp_path / "test_notif_db.json"
    temp_user_db = tmp_path / "test_user_db.json"

    temp_notif_db.write_text(json.dumps([]))
    temp_user_db.write_text(json.dumps({
        "Users": [
            {
                "id": 1,
                "username": "TestCustomer",
                "email": "testcustomer@123.com",
                "password": "Test@123",
                "role": Role.CUSTOMER.value, 
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 2,
                "username": "TestAdmin",
                "email": "testadmin@123.com",
                "password": "Test@123",
                "role": Role.ADMIN.value,
                "is_logged_in": False,
                "is_blocked": False
            }
        ]
    }))

    test_user_repo = UserRepository(file=str(temp_user_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))

    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_admin_service = AdminService()

    test_auth_controller = AuthController(
        repo=test_user_repo, 
        service=test_admin_service,
        notif_controller=test_notif_controller
    )

    app.dependency_overrides[get_controller] = lambda: test_auth_controller
    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo

    client = TestClient(app)
    client.headers.update({"X-User-Id": "2"})

    yield client, temp_notif_db

    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()

def test_block_user_notification(test_client):
    client, test_notif_db = test_client

    client.post("/auth/login", json={
        "email": "testadmin@123.com",
        "password": "Test@123"
    })
    response = client.post("/auth/blocked/TestCustomer")

    assert response.status_code == 200
    notifications = json.loads(test_notif_db.read_text())
    assert len(notifications) == 1
    assert notifications[0] ["user_id"] == 1
    assert notifications[0] ["type"] == NotificationType.BLOCKED_ACCOUNT.value
    assert notifications[0] ["is_read"] == False
    assert notifications[0] ["message"] == "Your account has been blocked by the administrator."

def test_unblock_user_notifications(test_client):
    client, test_notif_db = test_client
    client.post("/auth/login", json={
        "email": "testadmin@123.com",
        "password": "Test@123"
    })
    response = client.post("/auth/blocked/TestCustomer")
    assert response.status_code == 200

    response2 = client.delete("/auth/blocked/TestCustomer")
    assert response2.status_code == 200

    notifications = json.loads(test_notif_db.read_text())
    assert len(notifications) == 2
    assert notifications[0] ["type"] == NotificationType.BLOCKED_ACCOUNT.value

    assert notifications[1] ["user_id"] == 1
    assert notifications[1] ["type"] == NotificationType.UNBLOCKED_ACCOUNT.value
    assert notifications[1] ["is_read"] == False
    assert notifications[1] ["message"] == "Your account has been unblocked by the administrator."
