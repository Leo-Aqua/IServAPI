import json
import logging

from bs4 import BeautifulSoup


class Misc:
    def __init__(self, api) -> None:
        self.api = api

    def get_conference_health(self):
        """
        Get the health status of the conference API endpoint.

        :return: JSON response containing the health status of the API
        """
        health = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/videoconference/api/health"
        ).json()
        logging.info("Got Conference Health")
        return health

    def get_disk_space(self) -> dict:
        response = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/du/account"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        disk_json = soup.find("script", id="user-diskusage-data").get_text()
        disk_json = json.loads(disk_json.strip("()"))

        return disk_json
