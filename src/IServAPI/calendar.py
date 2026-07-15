import logging
from .classes import *
import dateutil
from bs4 import BeautifulSoup


class Calendar:
    def __init__(self, api) -> None:
        self.api = api

    def get_upcoming_events(self):
        """
        Retrieves the upcoming events from the IServ calendar API.

        :return: A JSON object containing the upcoming events.
        """
        events = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/calendar/api/upcoming"
        ).json()
        logging.info("Got upcomming events")
        return events

    def get_eventsources(self):
        """
        Retrieves the event sources from the calendar API.

        :return: A JSON object containing the event sources.
        """
        eventsources = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/calendar/api/eventsources"
        ).json()
        logging.info("Got eventsources")
        return eventsources

    def get_events(self, start: str, end: str):
        """Returns all events from all eventsources (Calendars) as a JSON object

        Args:
            start (str): Start date
            end (str): End date

        Returns:
            JSON: A JSON object with the data
        """

        events = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/calendar/feed/calendar-multi",
            params={
                "start": dateutil.parser.parse(start).strftime("%Y-%m-%d"),
                "end": dateutil.parser.parse(end).strftime("%Y-%m-%d"),
            },
        ).json()

        logging.info("Got calendar events")
        logging.debug(f"Got Calendar events from {start} to {end}")
        return events

    def search_event(self, query: str, start: str, end: str):
        """Searches for events in all eventsources

        Args:
            query (str): The search term
            start (str): The start date in any form parsable by dateutil. Time is also supported.
            end (str): The end date in any form parsable by dateutil. Time is also supported.

        Returns:
            JSON: All found events
        """
        events = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/calendar/api/lookup_event",
            params={
                "summary": query,
                "start": dateutil.parser.parse(start, yearfirst=True).isoformat(
                    timespec="microseconds"
                )[:-3]
                + "Z",  # Used to get this: 2025-09-24T22:59:59.999Z format
                "end": dateutil.parser.parse(end, yearfirst=True).isoformat(
                    timespec="microseconds"
                )[:-3]
                + "Z",
            },
        )
        logging.info("Looked up calendar events")
        logging.debug(
            f"Looked up Calendar events with query {query} from {start} to {end}"
        )
        return events.json()

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
        events = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/calendar/feed/plugin",
            params={
                "plugin": plugin,
                "start": dateutil.parser.parse(start).isoformat(),
                "end": dateutil.parser.parse(end).isoformat(),
            },
        )
        logging.debug(f"Got {plugin} envents from {start} to {end}")
        logging.info("Got calendar plugin events")
        return events.json()

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

        events = self.api._session.post(
            f"https://{self.api.iserv_url}/iserv/calendar/delete",
            params={
                "uid": uid,
                "hash": _hash,
                "cal": calendar,
                "start": dateutil.parser.parse(start).strftime("%Y-%m-%dT%H:%M:%S%z"),
                "edit_series": "series" if series else "single",
            },
        )
        logging.debug(f"Deleted event {uid} with hash {_hash} in calendar {calendar}")
        logging.debug(f"Status code: {events.status_code}")
        logging.info("Event deleted")
        return events.json()

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

        token_request = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/calendar/create_simple",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
        )
        tokensoup = BeautifulSoup(
            token_request.text, "html.parser"
        )  # , Ahh my favourite kind of soup

        token = tokensoup.find("input", {"id": "eventForm__token"}).get("value")

        # Minimal data
        data = {
            "eventForm[uid]": "",
            "eventForm[etag]": "",
            "eventForm[hash]": "",
            "eventForm[calendarOrg]": "",
            "eventForm[startOrg]": "",
            "eventForm[action]": "create",
            "eventForm[seriesAction]": "",
            "eventForm[invited]": "",
            "eventForm[subscription]": "",
            "eventForm[subject]": subject,
            "eventForm[calendar]": calendar,
            "eventForm[category]": category,
            "eventForm[location]": location,
            "eventForm[startDate]": dateutil.parser.parse(start).strftime("%d.%m.%Y"),
            "eventForm[startTime]": dateutil.parser.parse(start).strftime("%H:%M"),
            "eventForm[endDate]": dateutil.parser.parse(end).strftime("%d.%m.%Y"),
            "eventForm[endTime]": dateutil.parser.parse(end).strftime("%H:%M"),
            "eventForm[description]": description,
            "eventForm[showMeAs]": show_me_as,
            "eventForm[privacy]": privacy,
            "eventForm[recurring][intervalType]": "NO",
            "eventForm[recurring][interval]": "1",
            "eventForm[recurring][recurrenceDays][]": "FR",
            "eventForm[recurring][monthlyIntervalType]": "BYMONTHDAY",
            "eventForm[recurring][monthDayInMonth]": "26",
            "eventForm[recurring][endType]": "NEVER",
            "eventForm[submit]": "",
            "eventForm[_token]": token,
        }
        # Get Params ready
        # recurring = {
        #     "intervalType": "NO/DAILY/WEEKDAYS/WEEKLY/MONTHLY/YEARLY",
        #     "interval": 1 - 30,  # Not when WEEKDAYS is selected
        #     "monthlyIntervalType": "BYMONTHDAY/BYDAY",  # When MONTHLY is selected
        #     "monthDayInMonth": 1-31 # When BYMONTHDAY.
        #     "monthInterval": "1/2/3/4/-1",  # Every n'th day -1 is last When BYDAY is selected
        #     "monthDay": "MO/TU/WE/TH/FR/SA/SU",  # When BYDAY is selected
        #     "recurrenceDays": "MO/TU/WE/TH/FR/SA/SU",  # When WEEKLY is selected
        #     "endType": "NEVER/COUNT/UNTIL",
        #     "endInterval": int,  # When COUNT is selected
        #     "untilDate": "DD.MM.YYYY",  # When UNTIL is slected
        # }

        if recurring != {}:
            # Check values
            if "intervalType" not in recurring:
                raise ValueError("intervalType must be present!")
            if (
                recurring["intervalType"] != "WEEKDAYS"
                and recurring["intervalType"] != "NO"
                and "interval" not in recurring
            ):
                raise ValueError("interval must be present!")

            if "interval" in recurring:
                if recurring["interval"] not in range(1, 31):
                    raise ValueError("Interval can only be between 1 and 30")
            if recurring["intervalType"] == "MONTHLY":
                if "monthlyIntervalType" not in recurring:
                    raise ValueError("monthlyIntervalType must be present!")
                if recurring["monthlyIntervalType"] == "BYDAY":
                    if "monthInterval" not in recurring:
                        raise ValueError("monthInterval must be present!")
                    if "monthDay" not in recurring:
                        raise ValueError("monthDay must be present!")
                if recurring["monthlyIntervalType"] == "BYMONTHDAY":
                    if "monthDayInMonth" not in recurring:
                        raise ValueError("monthDayInMonth must be present!")
            if recurring["intervalType"] == "WEEKLY":
                if "recurrenceDays" not in recurring:
                    raise ValueError("recurrenceDays must be present!")
            if recurring["intervalType"] != "NO":
                if "endType" not in recurring:
                    raise ValueError("endType must be present!")

                if recurring["endType"] == "COUNT":
                    if "endInterval" not in recurring:
                        raise ValueError("endInterval must be present!")

                if recurring["endType"] == "UNTIL":
                    if "untilDate" not in recurring:
                        raise ValueError("untilDate must be present!")
            # Set values
            try:
                data["eventForm[recurring][intervalType]"] = recurring["intervalType"]

            except KeyError:
                pass
            try:
                data["eventForm[recurring][interval]"] = recurring["interval"]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][monthlyIntervalType]"] = recurring[
                    "monthlyIntervalType"
                ]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][monthDayInMonth]"] = recurring[
                    "monthDayInMonth"
                ]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][monthInterval]"] = recurring["monthInterval"]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][monthDay]"] = recurring["monthDay"]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][recurrenceDays][]"] = recurring[
                    "recurrenceDays"
                ]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][endType]"] = recurring["endType"]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][endInterval]"] = recurring["endInterval"]
            except KeyError:
                pass
            try:
                data["eventForm[recurring][untilDate]"] = recurring["untilDate"]
            except KeyError:
                pass

        # Very fun alarm parser
        if alarms != []:
            for i, alarm in enumerate(alarms):
                if isinstance(
                    alarm, str
                ):  # Check for anything that's a string but not a valid timed alarm.
                    if alarm not in [
                        "0M",
                        "5M",
                        "15M",
                        "30M",
                        "1H",
                        "2H",
                        "12H",
                        "1D",
                        "2D",
                        "7D",
                    ]:
                        raise ValueError(
                            "At least one timed alarm is not one of 0M,5M,15M,30M,1H,2H,12H,1D,2D or 7D."
                        )
                    else:  # Add timed alarm
                        data[f"eventForm[alarms][{i}][trigger][type]"] = (
                            f"PT{alarm}"  # Add alarm itself
                        )

                        data[f"eventForm[alarms][{i}][trigger][interval][days]"] = "0"
                        data[f"eventForm[alarms][{i}][trigger][interval][hours]"] = "0"
                        data[f"eventForm[alarms][{i}][trigger][interval][minutes]"] = (
                            "15"
                        )
                        data[f"eventForm[alarms][{i}][trigger][before]"] = "1"
                        data[f"eventForm[alarms][{i}][trigger][dateTime]"] = str(
                            dateutil.parser.parse(start).strftime("%d.%m.%Y+00:00")
                        )

                if isinstance(alarm, dict):  # Check for the two custom alarm types
                    if "custom_date_time" in alarm:
                        if (
                            "dateTime" not in alarm["custom_date_time"]
                        ):  # Check if dateTime exists. This does not check for a valid value, which is a flaw, but I trust the other devs and the date parser.
                            raise ValueError(
                                "custom_date_time alarm dict is malformed."
                            )

                        data[f"eventForm[alarms][{i}][trigger][type]"] = (
                            "custom_date_time"
                        )
                        data[f"eventForm[alarms][{i}][trigger][interval][days]"] = "0"
                        data[f"eventForm[alarms][{i}][trigger][interval][hours]"] = "0"
                        data[f"eventForm[alarms][{i}][trigger][interval][minutes]"] = (
                            "15"
                        )
                        data[f"eventForm[alarms][{i}][trigger][before]"] = "1"
                        data[f"eventForm[alarms][{i}][trigger][dateTime]"] = (
                            str(  # This is the only value being used the other ones are junk but still needed or iserv will complain
                                dateutil.parser.parse(
                                    alarm["custom_date_time"]["dateTime"]
                                ).strftime("%d.%m.%Y %H:%M")
                            )
                        )

                    else:
                        ValueError("Alarm dict malformed! Missing: custom_date_time")

                    if (
                        "custom_interval" in alarm
                    ):  # Same issue here. I Could fix it but I'm tired and doing this in my free time so glhf :)
                        if "interval" in alarm["custom_interval"]:
                            if not all(
                                x in alarm["custom_interval"]["interval"]
                                for x in ["days", "hours", "minutes"]
                            ):  # Check if not all three strings are in alarm["custom_interval"]
                                raise ValueError(
                                    "the `inteval` dict in `custom_interval` in alarms is malformed."
                                )

                        if "before" not in alarm["custom_interval"]:
                            raise ValueError("custom_interval needs a `before` key.")

                        data[f"eventForm[alarms][{i}][trigger][type]"] = (
                            "custom_interval"
                        )
                        data[f"eventForm[alarms][{i}][trigger][interval][days]"] = str(
                            alarm["custom_interval"]["interval"]["days"]
                        )  # Used
                        data[f"eventForm[alarms][{i}][trigger][interval][hours]"] = str(
                            alarm["custom_interval"]["interval"]["hours"]
                        )  # Used
                        data[f"eventForm[alarms][{i}][trigger][interval][minutes]"] = (
                            str(alarm["custom_interval"]["interval"]["minutes"])
                        )
                        data[f"eventForm[alarms][{i}][trigger][before]"] = (
                            "1" if alarm["custom_interval"]["before"] else "0"
                        )  # Used
                        data[f"eventForm[alarms][{i}][trigger][dateTime]"] = str(
                            dateutil.parser.parse(start).strftime("%d.%m.%Y+00:00")
                        )  # Ignored
                    else:
                        ValueError("Alarm dict malformed! Missing: custom_interval")

        # Actually simple participant parser
        if participants != []:
            for i, participant in enumerate(participants):
                try:
                    participants[i] = self.api.search_users_autocomplete(
                        participant, 1
                    )[0]["value"]
                except IndexError:
                    raise Exception(f"User `{participant}` not found!")

        data["eventForm[participants][]"] = participants

        # data = urllib.parse.urlencode(data)
        response = self.api._session.post(
            f"https://{self.api.iserv_url}/iserv/calendar/create",
            data=data,
            params={
                "subject": subject,
                "calendar": calendar,
                "start": dateutil.parser.parse(start).strftime("%d.%m.%Y"),
                "end": dateutil.parser.parse(end).strftime("%d.%m.%Y"),
                "startTime": dateutil.parser.parse(start).strftime("%H:%M"),
                "endTime": dateutil.parser.parse(end).strftime("%H:%M"),
                "allDay": isAllDayLong,
            },
        )

        eventsoup = BeautifulSoup(response.text, "html.parser")
        try:
            error = eventsoup.find("div", {"data-type": "error"})
            print(error.text)
        except AttributeError:
            pass
