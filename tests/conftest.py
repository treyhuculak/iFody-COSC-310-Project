import json
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.routers.orders import get_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.controllers.notification_controller import NotificationController

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/order.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test.json"
    temp_db.write_text(json.dumps([]))

    temp_notif_db = tmp_path / "test_notifications.json"
    temp_notif_db.write_text(json.dumps([]))

    test_repo = OrderRepository(file_path=str(temp_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))

    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_controller = OrderController(repo=test_repo, notif_controller=test_notif_controller)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()