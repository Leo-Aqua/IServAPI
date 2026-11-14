# Unofficial IServ API

This Python module allows you to interact with IServ school servers using only login data for authentication. No API key is required.

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Leo-Aqua/IServAPI) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Leo-Aqua/IServAPI/total?label=GitHub%20Downloads)
![PyPI - Downloads](https://img.shields.io/pypi/dm/IServAPI?label=PyPi%20Downloads)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/IServAPI) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/IServAPI) ![GitHub repo size](https://img.shields.io/github/repo-size/Leo-Aqua/IServAPI) ![PyPI - Version](https://img.shields.io/pypi/v/IServAPI?label=version)
![GitHub Repo stars](https://img.shields.io/github/stars/Leo-Aqua/IServAPI)



## Installation

```bash
pip install IServAPI
```


## Basic usage

```python
from IServAPI import IServAPI

# Initialize IServ instance with login credentials
api = IServAPI(username="YOUR_ISERV_USERNAME",password="YOUR_ISERV_PASSWORD", iserv_url="some_iserv_url.de")

# Example: Get the current user's information
user_info = api.get_own_user_info()

print(user_info)
```

If two-factor authentication is enabled for your account, pass the current code, or a function that returns it (it is only called if IServ asks for a code):

```python
api = IServAPI(
    username="YOUR_ISERV_USERNAME",
    password="YOUR_ISERV_PASSWORD",
    iserv_url="some_iserv_url.de",
    two_factor_code=lambda: input("Two-factor code: "),
)
```


## Table of contents

- [Unofficial IServ API](#unofficial-iserv-api)
  - [Installation](#installation)
  - [Basic usage](#basic-usage)
  - [Table of contents](#table-of-contents)
  - [Supported Functionality](#supported-functionality)
    - ### Own account
      - [Get own User Information](#get-own-user-information)
      - [Set own User Information](#set-own-user-information)
      - [Fetch notifications](#fetch-notifications)
      - [Get badges](#get-badges)
      - [Read all notifications](#read-all-notifications)
      - [Read a specific Notification](#read-a-specific-notification)
      - [Get disk space](#get-disk-space)
    - ### Users
      - [Get user avatar](#get-user-avatar)
      - [Search users](#search-users)
      - [Search users autocomplete](#search-users-autocomplete)
      - [Get other users information](#get-other-users-information)
    - ### Email
      - [Get mailboxes](#get-mailboxes)
      - [Get messages](#get-messages)
      - [Get a message](#get-a-message)
      - [Get emails](#get-emails)
      - [Get general Information about emails](#get-general-information-about-emails)
      - [Get email source](#get-email-source)
      - [Get all mail folders](#get-all-mail-folders)
      - [Send Email](#send-email)
    - ### Calendar
      - [Get upcoming events](#get-upcoming-events)
      - [Get all eventsources](#get-all-eventsources)
      - [Get events](#get-events)
      - [Get events of one calendar](#get-events-of-one-calendar)
      - [Search event](#search-for-events)
      - [Get plugin events](#get-events-by-plugin)
      - [Delete event](#delete-event)
      - [Create event](#create-event)
    - ### Misc
      - [Get conference health](#get-conference-health)
      - [Files](#files)
      - [Get folder size](#get-folder-size)
      - [Get groups](#get-groups)
    - [Logging](#logging)
    - [To-Do List](#to-do-list)
  - [Contribution](#contribution)
  - [Credits](#credits)
  - [License](#license)



## Supported Functionality

### Own account

#### Get own User Information

```python
user_info = get_own_user_info()
```

This method retrieves information about the currently logged-in user.

#### Set own User Information

```python
set_own_user_info(key=value)
```

This method sets your personal information

Available keys are:

`title`

`company`

`birthday`

`nickname`

`_class`

`street`

`zipcode`

`city`

`country`

`phone`

`mobilePhone`

`fax`

`mail`

`homepage`

`icq`

`jabber`

`msn`

`skype`

`note`


#### Fetch notifications

```python
notifications = get_notifications()
```

Retrieves notifications from the specified URL and returns them as a JSON object.


#### Get badges

```python
badges = get_badges()
```

Retrieves the badges from the IServ server. (Badges=numbers on sidebar)


#### Read all notifications

```python
read_all_notifications()
```

Marks all Notification as read.


#### Read a specific Notification

```python
read_notification(notification_id)
```

Marks a single notification as read.


#### Get disk space

```python
get_disk_space()
```
Returns information, like free disk space, label and color about all storage volumes accessible to you. (Windows account, Cloud, etc.)

---

### Users

#### Get user avatar

```python
get_user_profile_picture(user, output_folder)
```

This method retrieves the avatar of any user on the network

It saves the avatar in the folder followed by the username,


#### Search users

```python
search_users(query)
```


#### Search users autocomplete

```python
users = search_users_autocomplete(query, limit=50)
```

Faster than `search_users()` but may not display all users


#### Get other users information

```python
get_user_info(user)
```

Get someone else's public information this includes everything they heve set in 'Personal Information'


---

### Email

#### Get mailboxes

```python
mailboxes = get_mailboxes(account=None)
```

Retrieves all mail folders with unread and total counts (mail API v2). `account` defaults to the own mail address (read from the IServ mail app, falling back to `<username>@<iserv_url>`).


#### Get messages

```python
messages = get_messages(path="INBOX", limit=50, offset=0, sort="date", order="desc", query=None, search_fields=("subject", "from", "to"), account=None)
```

Retrieves the messages of a mail folder (mail API v2). With `query` the messages are searched in `search_fields`; add `"body"` for a (slower) full text search.


#### Get a message

```python
message = get_message(uid, path="INBOX", account=None)
```

Retrieves a single message with envelope, plain/HTML content and attachment list (mail API v2).


#### Get emails

```python
emails = get_emails(path = 'INBOX', length = 50, start = 0, order = 'date', dir = 'desc')
```

Retrieves emails from a specified path with optional parameters for length, start, order, and direction.


#### Get general Information about emails

```python
email_info = get_email_info(path="INBOX", length=0, start=0, order="date", dir="desc")
```

Retrieves email information from the specified path in the mailbox. For example: unread emails. **Deprecated:** use `get_messages()` or `get_mailboxes()`.


#### Get email source

```python
email_source = get_email_source(uid, path="INBOX")
```

Retrieves the source code of an email message from the specified email path and message ID.


#### Get all mail folders

```python
mail_folders = get_mail_folders()
```

Retrieves the list of mail folders. **Deprecated:** use `get_mailboxes()`.


#### Send Email

```python
send_email(receiver_email:str, subject:str, body:str, html_body:str=None, smtp_server:str=None, smtps_port:int=465, attachments:list=None)
```

Sends an email. Note all variables defaulting to none get defined later so don't worry.

sender_email must be a valid name present in the iserv network.


---

### Calendar

#### Get upcoming events

```python
events = get_upcoming_events()
```

Retrieves the upcoming events from the IServ calendar API.


#### Get events

```python
events = get_events(start="2024-01-01", end="2025-12-31", calendars=None)
```

Retrieves all events of all calendars (or only the given calendar IDs) in the specified timeframe.


#### Get events of one calendar

```python
events = get_calendar_appointments(calendar="/my.iserv.account/home", start="2024-01-01", end="2025-12-31")
```

Retrieves the events of a single calendar. Calendar IDs are returned by `get_eventsources()`.


---

#### Search for events

```python
events = search_event(query="Party", start="2024-01-01", end="2025-12-31")
```

Searches for an event in the specified timeframe.


---

#### Get events by Plugin

```python
events = api.get_calendar_plugin_events(
    "holiday",
    "2024.11.11",
    "2026.11.11"
)
```

Lists all events produced by a plugin. Plugins can be retrieved from the output of [`get_eventsources()`](#get-all-eventsources) where `id` is the plugin id if the `type` is `plugin`.


---

#### Get all eventsources

```python
eventsources = get_eventsources()
```

Retrieves the event sources from the calendar API.


---



#### Delete event

```python
status = delete_event(
  uid="XXXXXXXXXXXXXX@iservserver.de",
  _hash="541f2d74099d785d1286c03903a2e826",
  calendar="/my.iserv.account/home",
  start="2025-09-25T16:00:00+02:00",
  series=True
  )
```

Deletes an event. All parameters, except series, are returned by [`get_events()`](#get-events).

---

#### Create event

```python
create_event(
        subject = "Math exam",
        calendar: "/my.iserv.user/home",
        start: "27.09.2025 16:00",
        end: "28.09.2025 10:00",
        category: str = "exams",
        location: str = "school",
        alarms: = ["7D", "2D", "1D"],
        isAllDayLong: bool = False,
        description: str = "",
        participants: list = [],
        show_me_as: Literal["OPAQUE", "TRANSPARENT"] = "OPAQUE",
        privacy: Literal["PUBLIC", "CONFIDENTIAL", "PRIVATE"] = "PUBLIC",
        recurring: Recurring = {},
  )
```
Create a new event in the IServ calendar

This method constructs and submits an HTTP request to the IServ calendar API to create a new event with optional alarms, recurring patterns, and participants.

---

## Parameters

- **subject** (`str`):  
  The title or subject of the event.

- **calendar** (`str`):  
  The ID of the calendar where the event will be created.

- **start** (`str`):  
  Event start datetime in any format parsable by `dateutil.parser`.

- **end** (`str`):  
  Event end datetime in any format parsable by `dateutil.parser`.

- **category** (`str`, optional):  
  Category or tag for the event. Defaults to `""`.

- **location** (`str`, optional):  
  Location of the event. Defaults to `""`.

- **alarms** (`list[AlarmType]`, optional):  
  List of alarms for the event. Each alarm can be:
  - A string: `"0M"`, `"5M"`, `"15M"`, `"30M"`, `"1H"`, `"2H"`, `"12H"`, `"1D"`, `"2D"`, `"7D"`
  - A dictionary defining custom alarms:
    - **Custom datetime alarm**:  
      ```python  
      alarms = [{"custom_date_time": {"dateTime": "dd.mm.YYYY HH:MM"}}]  
      ```
    - **Custom interval alarm**:  
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
  Defaults to `[]`.

- **isAllDayLong** (`bool`, optional):  
  Whether the event lasts all day. Defaults to `False`.

- **description** (`str`, optional):  
  Detailed description of the event. Defaults to `""`.

- **participants** (`list`, optional):  
  List of participant identifiers (usernames or emails) to invite to the event. Defaults to `[]`.

- **show_me_as** (`Literal["OPAQUE", "TRANSPARENT"]`, optional):  
  Visibility of the event on your calendar.  
  - `"OPAQUE"` blocks time.  
  - `"TRANSPARENT"` shows availability.  
  Defaults to `"OPAQUE"`.

- **privacy** (`Literal["PUBLIC", "CONFIDENTIAL", "PRIVATE"]`, optional):  
  Privacy level of the event. Defaults to `"PUBLIC"`.

- **recurring** (`Recurring`, optional):  
  Dictionary defining recurring event rules. Example structure:  
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

---

## Notes

- All dates and times are automatically parsed and formatted to IServ's expected format.  
- The method prints any error messages returned by the IServ API.  

---

### Misc

#### Get conference health

```python
health = get_conference_health()
```

Get the health status of the conference API endpoint.


#### Files

```python
client = file()
```

Possible functions:

**Synchronous methods**

```python
# Checking existence of the resource

client.check("dir1/file1")
client.check("dir1")
```

```python
# Get information about the resource

client.info("dir1/file1")
client.info("dir1/")
```

```python
# Check free space

free_size = client.free()
```

```python
# Get a list of resources

files1 = client.list()
files2 = client.list("dir1")
```

```python
# Create directory

client.mkdir("dir1/dir2")
```

```python
# Delete resource

client.clean("dir1/dir2")
```

```python
# Copy resource

client.copy(remote_path_from="dir1/file1", remote_path_to="dir2/file1")
client.copy(remote_path_from="dir2", remote_path_to="dir3")
```

```python
# Move resource

client.move(remote_path_from="dir1/file1", remote_path_to="dir2/file1")
client.move(remote_path_from="dir2", remote_path_to="dir3")
```

```python
# Move resource

client.download_sync(remote_path="dir1/file1", local_path="~/Downloads/file1")
client.download_sync(remote_path="dir1/dir2/", local_path="~/Downloads/dir2/")
```

```python
# Unload resource

client.upload_sync(remote_path="dir1/file1", local_path="~/Documents/file1")
client.upload_sync(remote_path="dir1/dir2/", local_path="~/Documents/dir2/")
```

```python
# Publish the resource

link = client.publish("dir1/file1")
link = client.publish("dir2")
```

```python
# Unpublish resource

client.unpublish("dir1/file1")
client.unpublish("dir2")
```

```python
# Get the missing files

client.pull(remote_directory='dir1', local_directory='~/Documents/dir1')
```

```python
# Send missing files

client.push(remote_directory='dir1', local_directory='~/Documents/dir1')
```

**Asynchronous methods**

```python
# Load resource

kwargs = {
 'remote_path': "dir1/file1",
 'local_path':  "~/Downloads/file1",
 'callback':    callback
}
client.download_async(**kwargs)

kwargs = {
 'remote_path': "dir1/dir2/",
 'local_path':  "~/Downloads/dir2/",
 'callback':    callback
}
client.download_async(**kwargs)
```

```python
# Unload resource

kwargs = {
 'remote_path': "dir1/file1",
 'local_path':  "~/Downloads/file1",
 'callback':    callback
}
client.upload_async(**kwargs)

kwargs = {
 'remote_path': "dir1/dir2/",
 'local_path':  "~/Downloads/dir2/",
 'callback':    callback
}
client.upload_async(**kwargs)
```

For further informations visit [CloudPolis/webdav-client-python](https://github.com/CloudPolis/webdav-client-python)


#### Get folder size

```python
get_folder_size(path)
```

Returns the size of a folder in human readable form.

#### Get groups

```python
get_goups()
```
Returns a JSON object with all the group names as key and their ID as value.

---

## Logging

Add this
```python
IServAPI.setup_logging("app.log")
```
after your `from IServAPI import IServAPI`


---

## To-Do List

- [x] add search users
- [x] more functionality
- [ ] make wiki
- [ ] Add calendar modification capabilities 


---

## Contribution

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit

a pull request. Make sure to follow the existing code style and add appropriate tests for new functionality.

To run the tests:

```bash
pip install -r requirements-dev.txt
pytest
```


---

## Credits

- Author @Leo-Aqua  
- Author of [WebDAV client Python](https://github.com/CloudPolis/webdav-client-python) @CloudPolis


---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


> [!IMPORTANT]
> ## DISCLAIMER
> 
> I HOLD NO RESPONSIBILITY FOR ANY DAMAGES OR DATALOSS DONE BY THIS PACKAGE.
> 
> YOU ARE RESPONSIBLE FOR WHAT YOU DO!
