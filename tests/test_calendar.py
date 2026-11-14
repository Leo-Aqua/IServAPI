from unittest.mock import MagicMock
import pytest
from IServAPI.calendar import Calendar


@pytest.fixture
def mock_api():
    api = MagicMock()
    api.iserv_url = "iserv.example.com"
    api._session = MagicMock()
    return api


def _response(data):
    response = MagicMock()
    response.json.return_value = data
    return response


def test_get_calendar_appointments(mock_api):
    calendar = Calendar(api=mock_api)
    mock_api._session.get.return_value = _response([{"title": "Meeting"}])

    result = calendar.get_calendar_appointments(
        "/john.doe/home", "2026-01-01", "2026-01-31T12:00"
    )

    mock_api._session.get.assert_called_once_with(
        "https://iserv.example.com/iserv/calendar/api/calendar-appointments",
        params={"cal": "/john.doe/home", "start": "2026-01-01", "end": "2026-01-31"},
    )
    assert result == [{"title": "Meeting"}]


def test_get_events_queries_all_calendars(mock_api):
    calendar = Calendar(api=mock_api)
    eventsources = [
        {"id": "/john.doe/home", "type": "cal"},
        {"id": "/example.group/calendar", "type": "cal"},
        {"id": "holidays", "type": "plugin"},
    ]
    appointments = {
        "/john.doe/home": [{"title": "B", "start": "2026-01-02T10:00:00+01:00"}],
        "/example.group/calendar": [{"title": "A", "start": "2026-01-01T08:00:00+01:00"}],
    }

    def fake_get(url, params=None):
        if url.endswith("/iserv/calendar/api/eventsources"):
            return _response(eventsources)
        return _response(appointments[params["cal"]])

    mock_api._session.get.side_effect = fake_get

    result = calendar.get_events("2026-01-01", "2026-01-31")

    queried = [c.kwargs["params"]["cal"] for c in mock_api._session.get.call_args_list[1:]]
    assert queried == ["/john.doe/home", "/example.group/calendar"]  # plugins skipped
    assert [e["title"] for e in result] == ["A", "B"]  # sorted by start
    assert result[0]["calendar"] == "/example.group/calendar"


def test_get_events_with_explicit_calendars(mock_api):
    calendar = Calendar(api=mock_api)
    mock_api._session.get.return_value = _response([{"title": "X", "start": "2026-01-01"}])

    result = calendar.get_events("2026-01-01", "2026-01-31", calendars=["/john.doe/home"])

    mock_api._session.get.assert_called_once()  # no eventsources lookup
    assert result == [{"title": "X", "start": "2026-01-01", "calendar": "/john.doe/home"}]


def test_get_events_skips_failing_calendar_and_sorts_by_time(mock_api):
    calendar = Calendar(api=mock_api)
    appointments = {
        "/a/home": {"error": "Access denied"},
        "/b/home": [
            {"title": "later", "start": "2026-03-29T08:30:00+01:00"},  # 07:30 UTC
        ],
        "/c/home": [
            {"title": "earlier", "start": "2026-03-29T09:00:00+02:00"},  # 07:00 UTC
        ],
    }
    mock_api._session.get.side_effect = lambda url, params=None: _response(
        appointments[params["cal"]]
    )

    result = calendar.get_events(
        "2026-03-29", "2026-03-30", calendars=["/a/home", "/b/home", "/c/home"]
    )

    assert [e["title"] for e in result] == ["earlier", "later"]
