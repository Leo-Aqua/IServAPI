from IServAPI.notifications import Notifications
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_api():
    """Provides a cleanly mocked API core dependency for every test."""
    api = MagicMock()
    api.iserv_url = "school.iserv.de"
    api.username = "testuser"
    api._password = "securepassword"
    api._session = MagicMock()
    return api


def test_notifications(mock_api):
    notificatonClient = Notifications(api=mock_api)

    expected = """{
    "status": "success",
    "data": {
        "lastEventId": 0,
        "lastId": 1157927,
        "since": null,
        "count": 1,
        "notifications": [{
            "type": "mail",
            "id": 1157927,
            "groupId": "mail-14ce3dd3a49349bb0d25bee596d9870ab918b5b2",
            "groupTitle": "",
            "autoGrouping": false,
            "message": "E-Mail von user@demo.iserv.de",
            "groupMessage": "E-Mail von user@demo.iserv.de",
            "title": "asdf",
            "content": "",
            "trigger": null,
            "url": "/iserv/notification/goto/1157927",
            "icon": "envelope",
            "date": "2026-07-19T18:33:24+02:00",
            "publishAt": null,
            "published": true
        }]
    }
}"""

    mockResponse = MagicMock()

    mockResponse.json.return_value = expected
    mock_api._session.get.return_value = mockResponse

    result = notificatonClient.get_notifications()

    assert result == expected


def test_getBadges(mock_api):
    notificatonClient = Notifications(api=mock_api)

    expected = """{"mail":1}"""

    mockResponse = MagicMock()

    mockResponse.json.return_value = expected
    mock_api._session.get.return_value = mockResponse

    result = notificatonClient.get_badges()

    assert result == expected


def test_readAll(mock_api):
    notificatonClient = Notifications(api=mock_api)

    expected = """{"status":"success"}"""

    mockResponse = MagicMock()

    mockResponse.json.return_value = expected
    mock_api._session.post.return_value = mockResponse

    result = notificatonClient.read_all_notifications()

    assert result == expected


def test_readOneNotification(mock_api):
    notificatonClient = Notifications(api=mock_api)

    expected = """{"status":"success"}"""

    mockResponse = MagicMock()

    mockResponse.json.return_value = expected
    mock_api._session.post.return_value = mockResponse

    result = notificatonClient.read_notification(1234567)

    assert result == expected
