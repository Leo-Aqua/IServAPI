import logging


class Notifications:
    def __init__(self, api):
        self.api = api

    def get_notifications(self):
        """
        Retrieves notifications from the specified URL and returns them as a JSON object.
        """
        notifications = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/user/api/notifications"
        ).json()
        logging.info("Got Notifications")
        return notifications

    def get_badges(self):
        """
        Retrieves the badges from the IServ server.

        :return: A JSON object containing the badges.
        """
        badges = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/app/navigation/badges"
        ).json()
        logging.info("Got Badges")
        return badges

    def read_all_notifications(self):
        """
        Reads all notifications from the server.

        Returns:
            dict: A JSON object containing the status.

        Raises:
            requests.exceptions.RequestException: If there is an error while making the request.
        """
        notifications = self.api._session.post(
            f"https://{self.api.iserv_url}/iserv/notification/api/v1/notifications/readall",
        ).json()
        logging.info("Read all notifications")
        return notifications

    def read_notification(self, notification_id: int):
        """
        Sends a POST request to the IServ notification API to mark a specific notification as read.

        Args:
            notification_id (int): The ID of the notification to be marked as read. Note: notification_id can be returned from get_notifications()

        Returns:
            dict: The JSON response from the API call.

        Raises:
            requests.exceptions.RequestException: If there was an error making the API request.
        """
        notification = self.api._session.post(
            f"https://{self.api.iserv_url}/iserv/notification/api/v1/notifications/{notification_id}/read",
        ).json()
        logging.info("read notification " + str(notification_id))
        return notification
