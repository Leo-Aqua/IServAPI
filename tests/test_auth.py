from urllib.parse import parse_qs

import pytest
import requests
import requests_mock

from IServAPI.auth import AuthClient
from IServAPI.exceptions import AuthError

ISERV_URL = "iserv.example.com"
BASE = f"https://{ISERV_URL}"

LOGIN_PAGE = (
    '<form method="post" action="/iserv/auth/login">'
    '<input type="text" name="_username">'
    '<input type="password" name="_password">'
    '<input type="hidden" name="_csrf_token" value="login-token">'
    "</form>"
)
TWO_FACTOR_PAGE = (
    '<form method="post" action="/iserv/auth/twofactor/confirm">'
    + "".join(
        f'<input type="text" name="two_factor_login_form[two_factor_code_digit_{i}]">'
        for i in range(1, 7)
    )
    + '<input type="hidden" name="otp">'
    + '<input type="hidden" name="two_factor_login_form[_token]" value="2fa-token">'
    + "</form>"
)
# IServ completes the login with an HTML meta refresh
META_REFRESH = (
    '<html><head><meta http-equiv="refresh" '
    f'content="0;url={BASE}/iserv/app/authentication/redirect?code=abc&amp;state=xyz">'
    "</head></html>"
)


@pytest.fixture
def base_mock():
    """Context manager for requests_mock to ensure clean isolation per test."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def iserv(base_mock, monkeypatch):
    """Mocks a valid IServ server with a login form.

    requests_mock does not store response cookies in the session's cookie jar,
    so the client gets a known session and the login cookies are set on it
    when the final redirect target is requested.
    """
    session = requests.Session()
    monkeypatch.setattr("IServAPI.auth.requests.Session", lambda: session)
    monkeypatch.delenv("SKIP_ISERV_CHECK", raising=False)

    def set_login_cookies(request, context):
        session.cookies.set("IServSAT", "mocked_sat_token")
        session.cookies.set("IServSATId", "mocked_sat_id")
        session.cookies.set("IServSession", "mocked_session_id")
        return "<html>Dashboard</html>"

    base_mock.head(
        f"{BASE}/iserv/",
        status_code=302,
        headers={"Location": f"{BASE}/iserv/auth/auth?_iserv_app_url=%2Fiserv%2F"},
    )
    base_mock.get(f"{BASE}/iserv/auth/login", text=LOGIN_PAGE)
    base_mock.post(f"{BASE}/iserv/auth/login", text="<html>OK</html>")
    base_mock.get(f"{BASE}/iserv/", text=META_REFRESH)
    base_mock.get(
        f"{BASE}/iserv/app/authentication/redirect", text=set_login_cookies
    )
    return base_mock


def _form(request):
    return {key: values[0] for key, values in parse_qs(request.text).items()}


class TestAuth:

    def test_login_success(self, iserv):
        client = AuthClient("testuser", "correctpassword", ISERV_URL)

        # Assert tokens are processed and captured correctly
        assert client._IServSAT == "mocked_sat_token"
        assert client._IServSATId == "mocked_sat_id"
        assert client._IServSession == "mocked_session_id"

        # The credentials are submitted once, together with the hidden form fields
        login_posts = [
            r
            for r in iserv.request_history
            if r.method == "POST" and r.path == "/iserv/auth/login"
        ]
        assert len(login_posts) == 1
        assert _form(login_posts[0]) == {
            "_csrf_token": "login-token",
            "_username": "testuser",
            "_password": "correctpassword",
        }
        # The meta refresh is followed with the HTML entities decoded
        assert iserv.last_request.qs == {"code": ["abc"], "state": ["xyz"]}

    def test_login_failed_wrong_credentials(self, iserv):
        iserv.post(
            f"{BASE}/iserv/auth/login",
            text="Anmeldung fehlgeschlagen! Bitte überprüfen Sie Ihre Zugangsdaten.",
        )

        with pytest.raises(
            AuthError, match="Login failed! Probably wrong username or password."
        ):
            AuthClient(
                username="testuser", password="wrongpassword", iserv_url=ISERV_URL
            )

    def test_non_existent_url(self, base_mock):
        iserv_url = "thisurlwillhopefullyneverexist.local"

        # Mock a connection failure at the very first step
        base_mock.head(
            f"https://{iserv_url}/iserv/", exc=requests.exceptions.ConnectionError
        )

        # AuthClient re-raises connection problems as the built-in ConnectionError
        with pytest.raises(ConnectionError, match="Error establishing connection"):
            AuthClient("testuser", "password", iserv_url)

    def test_timeout_is_raised_as_connection_error(self, iserv):
        iserv.get(f"{BASE}/iserv/auth/login", exc=requests.exceptions.ReadTimeout)

        with pytest.raises(ConnectionError, match="Error establishing connection"):
            AuthClient("testuser", "password", ISERV_URL)

    def test_wrong_url_validation_failure(self, base_mock, monkeypatch):
        iserv_url = "google.com"
        # Ensure the safety check override env var is disabled for this test execution
        monkeypatch.delenv("SKIP_ISERV_CHECK", raising=False)

        # Mock a non-IServ response (wrong redirect destination)
        base_mock.head(
            f"https://{iserv_url}/iserv/",
            status_code=302,
            headers={"Location": "/not-an-iserv-path"},
        )

        with pytest.raises(
            AuthError,
            match=r"Could not validate IServ.*SKIP_ISERV_CHECK",
        ):
            AuthClient("testuser", "password", iserv_url)

    def test_server_check_rejects_non_redirect(self, base_mock, monkeypatch):
        iserv_url = "www.example.com"
        monkeypatch.delenv("SKIP_ISERV_CHECK", raising=False)
        # An ordinary website answers /iserv/ without redirecting to the IServ login
        base_mock.head(f"https://{iserv_url}/iserv/", status_code=200)

        with pytest.raises(AuthError, match="Could not validate IServ server"):
            AuthClient("testuser", "password", iserv_url)


@pytest.fixture
def two_factor_iserv(iserv):
    """Mocks an IServ login flow that asks for the two-factor code 123456."""
    iserv.post(f"{BASE}/iserv/auth/login", text=TWO_FACTOR_PAGE)

    def confirm(request, context):
        if _form(request).get("otp") == "123456":
            return META_REFRESH
        return TWO_FACTOR_PAGE  # code rejected: the form is shown again

    return iserv.post(f"{BASE}/iserv/auth/twofactor/confirm", text=confirm)


class TestTwoFactor:

    def test_login_with_code(self, two_factor_iserv):
        client = AuthClient("testuser", "password", ISERV_URL, two_factor_code="123 456")

        assert client._IServSession == "mocked_session_id"
        form = _form(two_factor_iserv.last_request)
        assert form["otp"] == "123456"
        assert form["two_factor_login_form[two_factor_code_digit_1]"] == "1"
        assert form["two_factor_login_form[two_factor_code_digit_6]"] == "6"
        assert form["two_factor_login_form[_token]"] == "2fa-token"

    def test_login_with_code_callback(self, two_factor_iserv):
        client = AuthClient(
            "testuser", "password", ISERV_URL, two_factor_code=lambda: "123456"
        )

        assert client._IServSAT == "mocked_sat_token"

    def test_two_factor_form_behind_meta_refresh(self, iserv):
        iserv.post(
            f"{BASE}/iserv/auth/login",
            text=f'<meta http-equiv="refresh" content="0;url={BASE}/iserv/auth/twofactor/confirm">',
        )
        iserv.get(f"{BASE}/iserv/auth/twofactor/confirm", text=TWO_FACTOR_PAGE)
        confirm = iserv.post(f"{BASE}/iserv/auth/twofactor/confirm", text=META_REFRESH)

        AuthClient("testuser", "password", ISERV_URL, two_factor_code="123456")

        assert confirm.called_once

    def test_missing_code(self, two_factor_iserv):
        with pytest.raises(AuthError, match="two_factor_code"):
            AuthClient("testuser", "password", ISERV_URL)

    def test_rejected_code(self, two_factor_iserv):
        with pytest.raises(AuthError, match="rejected"):
            AuthClient("testuser", "password", ISERV_URL, two_factor_code="654321")

    def test_wrong_number_of_digits(self, two_factor_iserv):
        with pytest.raises(AuthError, match="6 digits"):
            AuthClient("testuser", "password", ISERV_URL, two_factor_code="12345")

    def test_integer_code_is_rejected(self, two_factor_iserv):
        with pytest.raises(AuthError, match="must be a string"):
            AuthClient("testuser", "password", ISERV_URL, two_factor_code=123456)

    def test_callback_not_called_without_two_factor(self, iserv):
        def must_not_be_called():
            raise AssertionError("two_factor_code callback was called")

        AuthClient("testuser", "password", ISERV_URL, two_factor_code=must_not_be_called)
