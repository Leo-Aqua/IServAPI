from turtle import st

from .core import Core
from .profile import Profile
from .notifications import Notifications
from .users import Users
from .emails import Emails
from .calendar import Calendar
from .misc import Misc
from .files import Files


class IServAPI:

    # Technical

    def __init__(self, username, password, iserv_url):
        """
        Initializes the credentials and URLs needed for accessing the IServ system.

        :param username: str - The username for the IServ system.
        :param password: str - The password for the IServ system.
        :param iserv_url: str - The URL of the IServ system.
        :return: None
        """
        core = Core(username, password, iserv_url)

        self.username = core.username
        self._password = core._password
        self.iserv_url = core.iserv_url

        # Log in to IServ

        self._session = core._session
        self._IServSAT = core._IServSAT
        self._IServSATId = core._IServSATId
        self._IServSession = core._IServSession
        self.__DAVclient = None

        # Initialize submodules

        self.profile = Profile(self)
        self.notifications = Notifications(self)
        self.users = Users(self)
        self.emails = Emails(self)
        self.calendar = Calendar(self)
        self.misc = Misc(self)
        self.files = Files(self)

    # Own account

    def get_own_user_info(self):
        return self.profile.get_own_user_info()

    def set_own_user_info(self, **settings):
        """
        Sets the user's own information with the provided settings.

        :param settings: The settings to be applied to the user's information.
        :type settings: dict
        :Keyword Arguments:
            * *title* (``str``) -- The title of the user.
            * *company* (``str``) -- The company of the user.
            * *birthday* (``str``) -- The birthday of the user.
            * *nickname* (``str``) -- The nickname of the user.
            * *_class* (``str``) -- The class of the user.
            * *street* (``str``) -- The street of the user's address.
            * *zipcode* (``str``) -- The zipcode of the user's address.
            * *city* (``str``) -- The city of the user.
            * *country* (``str``) -- The country of the user.
            * *phone* (``str``) -- The phone number of the user.
            * *mobilePhone* (``str``) -- The mobile phone number of the user.
            * *fax* (``str``) -- The fax number of the user.
            * *mail* (``str``) -- The email address of the user.
            * *homepage* (``str``) -- The homepage of the user.
            * *icq* (``str``) -- The ICQ number of the user.
            * *jabber* (``str``) -- The Jabber ID of the user.
            * *msn* (``str``) -- The MSN ID of the user.
            * *skype* (``str``) -- The Skype ID of the user.
            * *note* (``str``) -- The note about the user.

        :return: The status code of the response from the server after setting the user information.
        :rtype: int
        """

        return self.profile.set_own_user_info(**settings)

    def get_notifications(self):
        """
        Retrieves notifications from the specified URL and returns them as a JSON object.
        """
        return self.notifications.get_notifications()

    def get_badges(self):
        """
        Retrieves the badges from the IServ server.

        :return: A JSON object containing the badges.
        """
        return self.notifications.get_badges()

    def read_all_notifications(self):
        """
        Reads all notifications from the server.

        Returns:
            dict: A JSON object containing the status.

        Raises:
            requests.exceptions.RequestException: If there is an error while making the request.
        """
        return self.notifications.read_all_notifications()

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
        return self.notifications.read_notification(notification_id)

    def get_disk_space(self) -> dict:
        return self.misc.get_disk_space()

    # Users

    def get_user_profile_picture(self, user, output_folder: str):
        """
        Retrieves the profile picture of a user and saves it to the specified output folder.

        This function checks if the user's avatar is in SVG format and saves it with the
        appropriate file extension, otherwise, it assumes the image is in WEBP format.

        Args:
            user (str): The username of the user whose profile picture is to be retrieved.
            output_folder (str): The directory path where the profile picture will be saved.

        """
        self.users.get_user_profile_picture(user, output_folder)

    def search_users(self, query):
        """
        Searches for users based on a query string and returns a list of dictionaries containing the user's name and URL.

        Args:
            query (str): The search query string.

        Returns:
            list: A list of dictionaries containing the user's name and URL.

        Raises:
            ValueError: If there are too many results and filter criteria need to be restricted.

        Example:
            >>> search_users("John")
            [{'name': 'john.doe', 'user_url': 'https://{iserv_url}/iserv/addressbook/public/show/john-doe'}, {'name': 'john.smith', 'user_url': '/iserv/addressbook/public/show/john.smith'}]
        """

        return self.users.search_users(query)

    def search_users_autocomplete(self, query, limit=50):
        """
        Perform autocomplete search for users based on the query and optional limit.

        Args:
            query (str): The search query.
            limit (int, optional): The maximum number of results to return. Defaults to 50.

        Returns:
            dict: The JSON response containing the list of users matching the query.
        """
        return self.users.search_users_autocomplete(query)

    def get_user_info(self, user):
        """
        A function to retrieve user information from a given URL and parse it into a dictionary.
        :param user: str - The user for who the information is being retrieved.
        :return: dict - A dictionary containing the user information.
        """
        return self.users.get_user_info(user)

    # Email

    def get_emails(self, path="INBOX", length=50, start=0, order="date", dir="desc"):
        """
        Retrieves emails from a specified path with optional parameters for length, start, order, and direction.

        Parameters:
            path (str): The path to retrieve emails from. Defaults to 'INBOX'.
            length (int): The number of emails to retrieve. Defaults to 50.
            start (int): The starting index for retrieving emails. Defaults to 0.
            order (str): The order in which emails are listed. Defaults to 'date'.
            dir (str): The direction of ordering, 'asc' for ascending and 'desc' for descending.

        Returns:
            dict: A JSON object containing the list of emails matching the specified criteria.
        """
        return self.emails.get_emails(path, length, start, order, dir)

    def get_email_info(self, path="INBOX", length=0, start=0, order="date", dir="desc"):
        """
        Retrieves email information from the specified path in the mailbox.

        Args:
            path (str, optional): The path in the mailbox to retrieve email information from. Defaults to "INBOX".
            length (int, optional): The number of email messages to retrieve. Defaults to 0 (retrieve all messages).
            start (int, optional): The index of the first email message to retrieve. Defaults to 0.
            order (str, optional): The column to order the email messages by. Defaults to "date".
            dir (str, optional): The direction of the ordering. Defaults to "desc" (descending).

        Returns:
            dict: A JSON object containing the email information.

        """
        return self.emails.get_email_info(path, length, start, order, dir)

    def get_email_source(self, uid, path="INBOX"):
        """
        Retrieves the source code of an email message from the specified email path and message ID.

        Args:
            uid (int): The unique identifier of the email message.
            path (str, optional): The path of the email folder. Defaults to "INBOX".

        Returns:
            str: The source code of the email message.
        """
        return self.emails.get_email_source(uid, path)

    def get_mail_folders(self):
        """
        Retrieves the list of mail folders from the IServ API.

        :return: A JSON object containing the list of mail folders.
        """
        return self.emails.get_mail_folders()

    def send_email(
        self,
        receiver_email: str,
        subject: str,
        body: str,
        html_body: str = None,
        smtp_server: str = None,
        smtps_port: int = 465,
        attachments: list = None,
    ):
        """
        Sends an email with the given parameters.

        Args:
            receiver_email (str): The email address of the recipient.
            subject (str): The subject of the email.
            body (str): The plain text body of the email.
            html_body (str, optional): The HTML body of the email. Defaults to None.
            smtp_server (str, optional): The SMTP server to use. If not provided, the default SMTP server will be used. Defaults to None.
            smtps_port (int, optional): The port to use for SMTPS. Defaults to 465.
            attachments (list, optional): A list of file paths of attachments to include in the email. Defaults to None.

        Raises:
            TypeError: If attachments is provided but is not a list.
            smtplib.SMTPException: If there is an error sending the email.

        Returns:
            None

        """

        self.emails.send_email(
            receiver_email,
            subject,
            body,
            html_body,
            smtp_server,
            smtps_port,
            attachments,
        )

    # Calendar

    def get_upcoming_events(self):
        """
        Retrieves the upcoming events from the IServ calendar API.

        :return: A JSON object containing the upcoming events.
        """
        return self.calendar.get_upcoming_events()

    def get_eventsources(self):
        """
        Retrieves the event sources from the calendar API.

        :return: A JSON object containing the event sources.
        """
        return self.calendar.get_eventsources()

    def get_events(self, start: str, end: str):
        """Returns all events from all eventsources (Calendars) as a JSON object

        Args:
            start (str): Start date
            end (str): End date

        Returns:
            JSON: A JSON object with the data
        """

        return self.calendar.get_events(start, end)

    def search_event(self, query: str, start: str, end: str):
        """Searches for events in all eventsources

        Args:
            query (str): The search term
            start (str): The start date in any form parsable by dateutil. Time is also supported.
            end (str): The end date in any form parsable by dateutil. Time is also supported.

        Returns:
            JSON: All found events
        """
        return self.calendar.search_event(query, start, end)

    def get_calendar_plugin_events(self, plugin: str, start: str, end: str):
        """Lists all events produced by a plugin.
        Plugins can be retrieved from the output of
        `get_eventsources()` where `id` is the plugin id if the `type` is `plugin`.

        Args:
            plugin (str): The name of the plugin
            start (str): The start date of the results
            end (str): The end date of the results

        Returns:
            JSON: Events
        """
        return self.calendar.get_calendar_plugin_events(plugin, start, end)

    def delete_event(
        self, uid: str, _hash: str, calendar: str, start: str, series: bool = False
    ):
        """Deletes a specified event or reocurring event series.

        Args:
            uid (str): uid of the event
            _hash (str): hash of the event
            calendar (str): calendar(_id) of the event
            start (str): The beginning date and time (add time if you are having trouble deleting single events)
            series (bool, optional): Delete reocurring events.

        Returns:
            JSON: Status
        """

        return self.calendar.delete_event(uid, _hash, calendar, start, series)

    def create_event(
        self,
        subject: str,
        calendar: str,
        start: str,
        end: str,
        category: str = "",
        location: str = "",
        alarms: list[AlarmType] = [],
        isAllDayLong: bool = False,
        description: str = "",
        participants: list = [],
        show_me_as: Literal["OPAQUE", "TRANSPARENT"] = "OPAQUE",
        privacy: Literal["PUBLIC", "CONFIDENTIAL", "PRIVATE"] = "PUBLIC",
        recurring: Recurring = {},
    ):
        """
        Create a new event in the IServ calendar.

        This method constructs and submits an HTTP request to the IServ calendar
        API to create a new event with optional alarms, recurring patterns,
        and participants.

        Parameters:
            subject (str): The title or subject of the event.

            calendar (str): The ID of the calendar where the event will be created.

            start (str): Event start datetime in any format parsable by `dateutil.parser`.

            end (str): Event end datetime in any format parsable by `dateutil.parser`.

            category (str, optional): Category or tag for the event. Defaults to "".

            location (str, optional): Location of the event. Defaults to "".

            alarms (list[AlarmType], optional): List of alarms for the event.
            Each alarm can be a string `("0M", "5M", "15M", "30M", "1H", "2H", "12H", "1D", "2D", "7D")`
            or a dictionary defining custom alarms (`custom_date_time` or `custom_interval`).
            custom_date_time must have this structure:
            ```python
            alarms = [{"custom_date_time": {"dateTime": "dd.mm.YYYY HH:MM"}}]
            ```
            custom_interval must have this structure:
            ```python
            alarms = [{
                "custom_interval": {
                    "interval": {
                        "days": int,
                        "hours": int,
                        "minutes": int,
                    },
                    "before": bool,
                }
            }]
            ```
            Defaults to [].

            isAllDayLong (bool, optional): Whether the event lasts all day. Defaults to False.

            description (str, optional): Detailed description of the event. Defaults to "".

            participants (list, optional): List of participant identifiers (usernames or emails)
                to invite to the event. Defaults to [].

            show_me_as (Literal["OPAQUE", "TRANSPARENT"], optional): Visibility of the event
                on your calendar. "OPAQUE" blocks time, "TRANSPARENT" shows availability.
                Defaults to "OPAQUE".

            privacy (Literal["PUBLIC", "CONFIDENTIAL", "PRIVATE"], optional): Privacy level
                of the event. Defaults to "PUBLIC".

            recurring (Recurring, optional): Dictionary defining recurring event rules.
                Structure:
                ```python
                    {
                        "intervalType": "NO|DAILY|WEEKDAYS|WEEKLY|MONTHLY|YEARLY",
                        "interval": int,           # Only for types other than NO/WEEKDAYS
                        "monthlyIntervalType": "BYMONTHDAY|BYDAY",  # Required for MONTHLY
                        "monthDayInMonth": int,    # Required if BYMONTHDAY
                        "monthInterval": str,      # Required if BYDAY
                        "monthDay": str,           # Day of week if BYDAY
                        "recurrenceDays": str,     # Comma-separated weekdays if WEEKLY
                        "endType": "NEVER|COUNT|UNTIL",
                        "endInterval": int,        # Required if COUNT
                        "untilDate": str           # Required if UNTIL, "DD.MM.YYYY"
                    }
                ```

        Raises:
            ValueError: If recurring or alarm parameters are malformed.
            Exception: If a participant cannot be found via autocomplete.

        Notes:
            - All dates and times are automatically parsed and formatted to IServ's expected format.
            - The method prints any error messages returned by the IServ API.
        """

        self.calendar.create_event(
            subject,
            calendar,
            start,
            end,
            category,
            location,
            alarms,
            isAllDayLong,
            description,
            participants,
            show_me_as,
            privacy,
            recurring,
        )

    # Misc

    def get_conference_health(self):
        """
        Get the health status of the conference API endpoint.

        :return: JSON response containing the health status of the API
        """
        return self.misc.get_conference_health()

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
        return self.files.file(davurl, username, password, path)

    def get_folder_size(self, path: str) -> dict:
        return self.files.get_folder_size(path)

    def get_groups(self) -> dict:

        return self.profile.get_groups()
