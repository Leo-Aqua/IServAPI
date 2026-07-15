import logging

import webdav3.client as wc
from webdav3.exceptions import WebDavException


class Files:
    def __init__(self, api) -> None:
        self.api = api

    def file(self, davurl="default", username="default", password="default", path="/"):
        """
        A function that initializes a WebDAV client with the provided or default credentials and returns the client object.

        Parameters:
            davurl (str): The WebDAV URL. Default is "default".
            username (str): The username for authentication. Default is "default".
            password (str): The password for authentication. Default is "default".
            path (str): The path for the WebDAV client. Default is "/".

        Returns:
            WebDAV client object: A WebDAV client object initialized with the provided or default credentials.
        """
        if wc is None:
            raise ImportError("webdavclient3 is required for file()")

        try:
            davurl = "webdav." + self.api.iserv_url if davurl == "default" else davurl
            username = self.api.username if username == "default" else username
            password = self.api._password if password == "default" else password
            options = {
                "webdav_hostname": "https://" + davurl,
                "webdav_login": username,
                "webdav_password": password,
            }
            self.__DAVclient = wc.Client(options)
            logging.info("Files initiated")
            return self.__DAVclient
        except WebDavException as e:
            logging.error("Exception at file (webdav): " + str(e))
            raise ValueError("Exception at file (webdav): " + str(e))

    def get_folder_size(self, path: str) -> dict:
        response = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/file/calc?path={path}"
        )
        return response.json()
