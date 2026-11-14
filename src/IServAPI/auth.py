import html
import logging
from dotenv import load_dotenv
import requests
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from . import exceptions
from os import getenv

# Seconds to wait for the IServ server before giving up on a request
TIMEOUT = 30

_DIGIT_FIELD = re.compile(r"digit_?(\d+)\]?$")
_META_REFRESH = re.compile(
    r"""<meta[^>]+http-equiv=["']?refresh["']?[^>]*content=["'][^"']*url=([^"'\s>]+)""",
    re.IGNORECASE,
)


class AuthClient:

    def __init__(
        self, username, password, iserv_url, two_factor_code=None
    ) -> None:
        self.username = username
        self._password = password
        self.iserv_url = iserv_url
        self._two_factor_code = two_factor_code
        self._session = requests.Session()
        self._IServSAT = None
        self._IServSATId = None
        self._IServSession = None

        self.login()

    def login(self):
        """
        Authenticates the user against the IServ server and initiates a session.

        This method performs a POST request with the user's credentials to the
        IServ authentication URL and checks for common failure scenarios such as
        non-existent accounts or failed login attempts due to wrong credentials.
        If the account uses two-factor authentication, the code passed as
        `two_factor_code` is submitted. Upon successful login, it retrieves session cookies.

        Raises:
            AuthError: If the login fails or a two-factor code is missing or rejected.
            ConnectionError: If there is a problem establishing a connection.
        """

        try:
            testIServResponse = self._session.head(
                f"https://{self.iserv_url}/iserv/", timeout=TIMEOUT
            )
            if getenv("SKIP_ISERV_CHECK") != "1":
                if (
                    testIServResponse.status_code != 302
                    or "/iserv/"
                    not in testIServResponse.headers.get("Location", "")
                ):
                    raise exceptions.AuthError(
                        "Could not validate IServ server. Set `SKIP_ISERV_CHECK` to 1 to skip this check."
                    )

            # Load the login form first: it sets the session cookies and may
            # contain hidden fields (e.g. a CSRF token) that must be sent back
            login_url = f"https://{self.iserv_url}/iserv/auth/login"
            login_page = self._follow_meta_refresh(
                self._session.get(login_url, timeout=TIMEOUT)
            )
            login_form = self._find_form(login_page.text, "_password")

            # Prepare login credentials to send with POST request
            login_data = {}
            if login_form is not None:
                login_data.update(self._hidden_fields(login_form))
                login_url = urljoin(
                    login_page.url, login_form.get("action") or login_page.url
                )
            login_data.update({"_username": self.username, "_password": self._password})

            # Submit login credentials and check response
            login_response = self._follow_meta_refresh(
                self._session.post(login_url, data=login_data, timeout=TIMEOUT)
            )

            # Check if the login has failed, usually due to incorrect credentials
            if "Anmeldung fehlgeschlagen!" in login_response.text:
                raise exceptions.AuthError(
                    "Login failed! Probably wrong username or password."
                )

            # Accounts with two-factor authentication get a second form
            two_factor_form = self._find_two_factor_form(login_response.text)
            if two_factor_form is not None:
                self._submit_two_factor_code(two_factor_form, login_response.url)

            # Retrieve and store session cookies after successful login
            self.get_cookies()

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as e:
            # Handle connection errors during the login process
            raise ConnectionError(f"Error establishing connection: {e}")

    def _follow_meta_refresh(self, response, max_hops=5):
        """Follows <meta http-equiv="refresh"> redirects, which IServ uses during login."""
        for _ in range(max_hops):
            match = _META_REFRESH.search(response.text)
            if match is None:
                break
            target = urljoin(response.url, html.unescape(match.group(1)))
            response = self._session.get(target, timeout=TIMEOUT)
        return response

    @staticmethod
    def _find_form(page, field_name):
        """Returns the first form containing an input whose name matches `field_name`."""
        soup = BeautifulSoup(page, "html.parser")
        for form in soup.find_all("form"):
            if form.find("input", attrs={"name": field_name}):
                return form
        return None

    @classmethod
    def _find_two_factor_form(cls, page):
        return cls._find_form(page, _DIGIT_FIELD) or cls._find_form(page, "otp")

    @staticmethod
    def _hidden_fields(form):
        return {
            field["name"]: field.get("value", "")
            for field in form.find_all("input", attrs={"type": "hidden"})
            if field.get("name")
        }

    def _submit_two_factor_code(self, form, page_url):
        code = self._two_factor_code
        if callable(code):
            code = code()
        if not code:
            raise exceptions.AuthError(
                "Two-factor authentication is enabled for this account. "
                "Pass the current code as `two_factor_code`."
            )
        if not isinstance(code, str):
            # An int would lose leading zeros
            raise exceptions.AuthError(
                'The two-factor code must be a string, e.g. "012345".'
            )
        code = code.replace(" ", "")
        if not code.isdigit():
            raise exceptions.AuthError("The two-factor code must only contain digits.")

        # Hidden fields (e.g. the CSRF token) are sent back unchanged
        data = self._hidden_fields(form)

        # IServ splits the code into one field per digit and copies the
        # whole code into the hidden field "otp" via JavaScript
        digit_fields = {}
        for field in form.find_all("input", attrs={"name": _DIGIT_FIELD}):
            if field.get("type", "text") != "hidden":
                position = int(_DIGIT_FIELD.search(field["name"]).group(1))
                digit_fields[position] = field["name"]
        if digit_fields:
            if len(digit_fields) != len(code):
                raise exceptions.AuthError(
                    f"The two-factor code must have {len(digit_fields)} digits."
                )
            for position, name in digit_fields.items():
                data[name] = code[position - 1]
        if "otp" in data or not digit_fields:
            data["otp"] = code

        action = urljoin(page_url, form.get("action") or page_url)
        response = self._follow_meta_refresh(
            self._session.post(action, data=data, timeout=TIMEOUT)
        )

        if self._find_two_factor_form(response.text) is not None:
            raise exceptions.AuthError("The two-factor code was rejected.")
        logging.info("Two-factor code accepted")

    def get_cookies(self):

        # Request to home page, which completes the login with a redirect
        home_url = f"https://{self.iserv_url}/iserv/"
        self._follow_meta_refresh(
            self._session.get(home_url, allow_redirects=True, timeout=TIMEOUT)
        )

        # Print out the cookies
        cookies = self._session.cookies.get_dict()
        self._IServSAT = cookies.get("IServSAT")
        self._IServSATId = cookies.get("IServSATId")
        self._IServSession = cookies.get("IServSession")
        if (
            self._IServSAT == None
            or self._IServSATId == None
            or self._IServSession == None
        ):
            raise exceptions.AuthError("Failed to login!")
        logging.info("Cookies extracted successfully!")
        return
