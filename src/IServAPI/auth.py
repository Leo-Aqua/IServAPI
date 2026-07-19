import logging
from dotenv import load_dotenv
import requests
import re
from . import exceptions
from os import getenv


class AuthClient:

    def __init__(self, username, password, iserv_url) -> None:
        self.username = username
        self._password = password
        self.iserv_url = iserv_url
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
        Upon successful login, it retrieves session cookies.

        Raises:
            ValueError: If the account does not exist or the login fails.
            ConnectionError: If there is a problem establishing a connection.
        """

        try:
            testIServResponse = self._session.head(f"https://{self.iserv_url}/iserv/")
            if getenv("SKIP_ISERV_CHECK") != "1":
                if (
                    testIServResponse.status_code != 302
                    and "/iserv/auth/auth?_iserv_app_url"
                    not in testIServResponse.headers
                ):
                    raise exceptions.AuthError(
                        "Could not validate IServ Sever set `SKIP_ISERV_CHECK` to 1 to skip this check"
                    )

            # Prepare login credentials to send with POST request
            login_data = {"_username": self.username, "_password": self._password}

            # Submit login credentials and check response
            login_response = self._session.post(
                f"https://{self.iserv_url}/iserv/auth/login", data=login_data
            )

            # Check if the login has failed, usually due to incorrect credentials
            if "Anmeldung fehlgeschlagen!" in login_response.text:
                raise exceptions.AuthError(
                    "Login failed! Probably wrong username or password."
                )

        except requests.exceptions.ConnectionError as e:
            # Handle connection errors during the login process
            raise ConnectionError(f"Error establishing connection: {e}")

        # Retrieve and store session cookies after successful login
        self.get_cookies()

    def get_cookies(self):

        # First request to login page
        login_url = f"https://{self.iserv_url}/iserv/auth/login"
        # headers = {
        #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        #     "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        #     "cache-control": "max-age=0",
        #     "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        #     "sec-ch-ua-mobile": "?0",
        #     "sec-ch-ua-platform": '"Windows"',
        #     "sec-fetch-dest": "document",
        #     "sec-fetch-mode": "navigate",
        #     "sec-fetch-site": "none",
        #     "sec-fetch-user": "?1",
        #     "upgrade-insecure-requests": "1",
        #     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        # }

        # Second request to submit login credentials
        login_data = {"_username": self.username, "_password": self._password}

        response = self._session.post(login_url, data=login_data)

        # Third request to home page
        home_url = f"https://{self.iserv_url}/iserv/"
        response = self._session.get(home_url, allow_redirects=True)
        match = re.search(r'url=([^"\s>]+)', response.text)

        redirect_url = match.group(1).replace("amp;", "")  # type: ignore
        # Follow redirect

        response = self._session.get(redirect_url)

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
