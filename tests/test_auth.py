import pytest
import requests_mock
from requests.exceptions import ConnectionError

from IServAPI.auth import AuthClient
from IServAPI.exceptions import AuthError


@pytest.fixture
def base_mock():
    """Context manager for requests_mock to ensure clean isolation per test."""
    with requests_mock.Mocker() as m:
        yield m


class TestAuth:

def test_login_success(self, base_mock):
        iserv_url = "demo.iserv.de"

        # 1. Mock host validation check.
        # CRITICAL: We pass complete URL strings for the Location headers 
        # so requests_mock knows exactly where the redirect goes.
        base_mock.head(
            f"https://{iserv_url}/iserv/",
            status_code=302,
            headers={"Location": f"https://{iserv_url}/iserv/auth/auth?_iserv_app_url"},
        )
        
        # 1b. Mock the target of that HEAD redirect (which requests converts to a GET)
        base_mock.get(
            f"https://{iserv_url}/iserv/auth/auth?_iserv_app_url",
            status_code=200
        )

        # 2 & 3. Mock both POST login submissions (one in login(), one in get_cookies())
        base_mock.post(
            f"https://{iserv_url}/iserv/auth/login",
            status_code=200,
            text="Erfolgreich"  # Clean response that doesn't contain "Anmeldung fehlgeschlagen!"
        )

        # 4. Mock the third request to the home page inside get_cookies()
        # This must return a meta-refresh tag matching your regex pattern re.search(r'url=([^"\s>]+)', ...)
        fake_redirect_target = f"https://{iserv_url}/iserv/dashboard"
        mock_home_html = f"""
        <html>
            <head><meta http-equiv="refresh" content="0;url={fake_redirect_target}"></head>
            <body>Redirecting...</body>
        </html>
        """
        base_mock.get(
            f"https://{iserv_url}/iserv/",
            status_code=200,
            text=mock_home_html
        )

        # 5. Mock the final redirect destination target that drops the session cookies
        base_mock.get(
            fake_redirect_target,
            status_code=200,
            cookies={
                "IServSAT": "mocked_sat_token",
                "IServSATId": "mocked_sat_id",
                "IServSession": "mocked_session_id",
            }
        )

        # Act
        client = AuthClient("testuser", "correctpassword", iserv_url)

        # Assert tokens are processed and captured correctly
        assert client._IServSAT == "mocked_sat_token"
        assert client._IServSATId == "mocked_sat_id"
        assert client._IServSession == "mocked_session_id"

    def test_login_failed_wrong_credentials(self, base_mock):
        iserv_url = "example.iserv.de"

        base_mock.head(
            f"https://{iserv_url}/iserv/",
            status_code=302,
            headers={"Location": "/iserv/auth/auth?_iserv_app_url"},
        )
        base_mock.post(
            f"https://{iserv_url}/iserv/auth/login",
            status_code=200,
            text="Anmeldung fehlgeschlagen! Bitte überprüfen Sie Ihre Zugangsdaten.",
        )

        with pytest.raises(
            AuthError, match="Login failed! Probably wrong username or password."
        ):
            AuthClient(
                username="testuser", password="wrongpassword", iserv_url=iserv_url
            )

    def test_non_existent_url(self, base_mock):
        iserv_url = "thisurlwillhopefullyneverexist.local"

        # Mock a connection failure at the very first step
        base_mock.head(f"https://{iserv_url}/iserv/", exc=ConnectionError)

        with pytest.raises(ConnectionError):
            AuthClient("testuser", "password", iserv_url)

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
