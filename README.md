# Unofficial IServ API

This Python module allows you to interact with IServ school servers using only login data for authentication. No API key is required.

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Leo-Aqua/IServAPI) ![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Leo-Aqua/IServAPI/total?label=GitHub%20Downloads)
 ![PyPI - Downloads](https://img.shields.io/pypi/dm/IServAPI?label=PyPi%20Downloads)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/IServAPI) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/IServAPI) ![GitHub repo size](https://img.shields.io/github/repo-size/Leo-Aqua/IServAPI) ![PyPI - Version](https://img.shields.io/pypi/v/IServAPI?label=version)
![GitHub Repo stars](https://img.shields.io/github/stars/Leo-Aqua/IServAPI)



## Installation

You can install the IServ Python module using pip:

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

## List of functions

1. [Get own User Information](#1-get-own-user-information)
2. [Set own User Information](#2-set-own-user-information)
3. [Get user avatar](#3-get-user-avatar)
4. [Get emails](#4-get-emails)
5. [Search users](#5-search-users)
6. [Search users autocomplete](#6-search-users-autocomplete)
7. [Fetch notifications](#7-fetch-notifications)
8. [Get general Information about emails](#8-get-general-information-about-emails)
9. [Get email source](#9-get-email-source)
10. [Get all mail folders](#10-get-all-mail-folders)
11. [Get upcoming events](#11-get-upcoming-events)
12. [Get all eventsources](#12-get-all-eventsources)
13. [Get conference health](#13-get-conference-health)
14. [Get badges](#14-get-badges)
15. [Files](#15-files)
16. [Read all notifications](#16-read-all-notifications)
17. [Read a specific Notification](#17-read-a-specific-notification)
18. [Send Email](#18-send-email)
19. [Get other users information](#19-get-other-users-information)



## Supported Functionality

### Get own User Information

```python
user_info = get_own_user_info()
```

This method retrieves information about the currently logged-in user.

### 2. Set own User Information

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


### 3. Get user avatar

```python
get_user_profile_picture(user, output_folder)
```

This method retrieves the avatar of any user on the network

It saves the avatar in the folder followed by the username,


### 4. Get emails

```python
emails = get_emails(path = 'INBOX', length = 50, start = 0, order = 'date', dir = 'desc')
```

Retrieves emails from a specified path with optional parameters for length, start, order, and direction.

### 5. Search users

```python
search_users(query)
```



### 6. Search users autocomplete

```python
users = search_users_autocomplete(query, limit=50)
```

Faster than `search_users()` but may not display all users

### 7. Fetch notifications

```python
notifications = get_notifications()
```

Retrieves notifications from the specified URL and returns them as a JSON object.


### 8. Get general Information about emails

```python
email_info = get_email_info(path="INBOX", length=0, start=0, order="date", dir="desc")
```

Retrieves email information from the specified path in the mailbox. For example: unread emails.


### 9. Get email source

```python
email_source = get_email_source(uid, path="INBOX")
```

Retrieves the source code of an email message from the specified email path and message ID.


### 10. Get all mail folders

```python
mail_folders = get_mail_folders()
```

Retrieves the list of mail folders.


### 11. Get upcoming events

```python
events = get_upcoming_events()
```

Retrieves the upcoming events from the IServ calendar API.


### 12. Get all eventsources

```python
eventsources = get_eventsources()
```

Retrieves the event sources from the calendar API.


### 13. Get conference health

```python
health = get_conference_health()
```

Get the health status of the conference API endpoint.


### 14. Get badges

```python
badges = get_badges()
```

Retrieves the badges from the IServ server. (Badges=numbers on sidebar)


### 15. Files

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


### 16. Read all notifications

```python
read_all_notifications()
```

Marks all Notification as read.


### 17. Read a specific Notification


```python
read_notifiaction(notification_id)
```

Marks a specified Message as read. Note: notification_id can be returned from get_notifications()


### 18. Send Email


```python
send_email(receiver_email:str, subject:str, body:str, html_body:str=None, smtp_server:str=None, smtps_port:int=465, sender_name:str=None, attachments:list=None, sender_email:str=None)
```

Sends an email. Note all variables defaulting to none get defined later so don't worry.

sender_email must be a valid name present in the iserv network.


### 19. Get other users information


```python
get_user_info(user)
```

Get someone else's public information this includes everything they heve set in 'Personal Information'

### Logging

Add this
```python
IServAPI.setup_logging("app.log")
```
after your `from IServAPI.IServAPI import IServAPI`


### To-Do List

- [x] add search users

- [x] more functionality

- [ ] make wiki

## Contribution

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit

a pull request. Make sure to follow the existing code style and add appropriate tests for new functionality.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

> [!IMPORTANT]
> ## DISCLAIMER
> I HOLD NO RESPONSIBILITY FOR ANY DAMAGES OR DATALOSS DONE BY THIS > PACKAGE. >YOU ARE RESPONSIBLE FOR YOUR DATA!
