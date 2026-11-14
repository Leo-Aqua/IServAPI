from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import json
import logging
import os
import smtplib
from urllib.parse import quote
import warnings

from bs4 import BeautifulSoup


class Emails:
    def __init__(self, api) -> None:
        self.api = api

    # Mail API v2 (used by the current IServ web mail client)

    @staticmethod
    def mailbox_id(path: str) -> str:
        """
        Converts a mailbox path (e.g. "INBOX" or "INBOX/Archive") into the mailbox ID used
        by the IServ mail API v2: the path encoded as URL-safe base64 without padding.

        Args:
            path (str): The mailbox path.

        Returns:
            str: The mailbox ID, e.g. "SU5CT1g" for "INBOX".
        """
        return base64.urlsafe_b64encode(path.encode("utf-8")).decode("ascii").rstrip("=")

    def get_mail_account(self) -> str:
        """
        Returns the mail address of the logged in user as reported by the IServ mail app.
        Falls back to "<username>@<iserv_url>" if it cannot be determined. The result is cached.

        Returns:
            str: The mail address.
        """
        if getattr(self, "_mail_account", None):
            return self._mail_account
        account = None
        try:
            valid_accounts = self.get_emails()["accounts"]["valid"]
            if valid_accounts:
                account = next(iter(valid_accounts))
        except Exception as e:
            logging.debug(f"Could not determine mail account: {e}")
        if not account:
            account = (
                self.api.username
                if "@" in self.api.username
                else f"{self.api.username}@{self.api.iserv_url}"
            )
        self._mail_account = account
        return account

    def _mail_account_url(self, account: str = None) -> str:
        if account is None:
            account = self.get_mail_account()
        return f"https://{self.api.iserv_url}/iserv/mail/api/v2/account/{quote(account, safe='@')}"

    def get_mailboxes(self, account: str = None):
        """
        Retrieves all mailboxes (folders) of a mail account, including unread and total counts.

        Args:
            account (str, optional): The mail address of the account. Defaults to `get_mail_account()`.

        Returns:
            dict: A JSON object containing the mailboxes.
        """
        mailboxes = self.api._session.get(
            f"{self._mail_account_url(account)}/mailbox"
        ).json()
        logging.info("Got mailboxes")
        return mailboxes

    def get_messages(
        self,
        path="INBOX",
        limit=50,
        offset=0,
        sort="date",
        order="desc",
        query: str = None,
        search_fields=("subject", "from", "to"),
        account: str = None,
    ):
        """
        Retrieves a list of messages from a mailbox.

        Args:
            path (str, optional): The mailbox path. Defaults to "INBOX".
            limit (int, optional): The number of messages to retrieve. Defaults to 50.
            offset (int, optional): The index of the first message. Defaults to 0.
            sort (str, optional): The field to sort by. Defaults to "date".
            order (str, optional): "asc" or "desc". Defaults to "desc".
            query (str, optional): A search term. Defaults to None (no search).
            search_fields (tuple, optional): The fields to search in when `query` is set.
                Add "body" for a full text search (can be slow on large mailboxes).
                Defaults to ("subject", "from", "to").
            account (str, optional): The mail address of the account. Defaults to `get_mail_account()`.

        Returns:
            dict: A JSON object with "items" (the messages), "total" and "offset".
        """
        params = {
            "mailbox[]": self.mailbox_id(path),
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "order": order,
        }
        if query:
            params["q"] = query
            # Without explicit search fields the IServ search may not respond at all
            if isinstance(search_fields, str):
                search_fields = [search_fields]
            params["query_search_fields[]"] = list(search_fields)

        messages = self.api._session.get(
            f"{self._mail_account_url(account)}/message", params=params
        ).json()
        logging.info("Got messages")
        return messages

    def get_message(self, uid, path="INBOX", account: str = None):
        """
        Retrieves a single message including its envelope, content and attachment list.

        Args:
            uid (int): The UID of the message.
            path (str, optional): The mailbox path. Defaults to "INBOX".
            account (str, optional): The mail address of the account. Defaults to `get_mail_account()`.

        Returns:
            dict: A JSON object with "envelope", "content" ("plain" and/or "rich" parts) and "attachments".
        """
        message = self.api._session.get(
            f"{self._mail_account_url(account)}/mailbox/{self.mailbox_id(path)}/message/{uid}"
        ).json()
        logging.info("Got message")
        return message

    # Legacy endpoints

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
        emails_html = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/mail/api/message/list?path={path}&length={str(length)}&start={str(start)}&order%5Bcolumn%5D={order}&order%5Bdir%5D={dir}"
        ).text
        email_soup = BeautifulSoup(emails_html, "html.parser")
        emails = email_soup.find("script", id="php-data").string.strip()
        emails = json.loads(emails)

        logging.info("Got emails sccessfully!")
        return emails

    def get_email_info(self, path="INBOX", length=0, start=0, order="date", dir="desc"):
        """
        Retrieves email information from the specified path in the mailbox.

        Deprecated:
            `/iserv/mail/api/message/list` only returns HTML on current IServ versions.
            This now returns the result of `get_messages()` (message list incl. "total").
            Use `get_messages()` or `get_mailboxes()` (unread counts) directly instead.

        Args:
            path (str, optional): The path in the mailbox to retrieve email information from. Defaults to "INBOX".
            length (int, optional): The number of email messages to retrieve. Defaults to 0 (only the totals).
            start (int, optional): The index of the first email message to retrieve. Defaults to 0.
            order (str, optional): The column to order the email messages by. Defaults to "date".
            dir (str, optional): The direction of the ordering. Defaults to "desc" (descending).

        Returns:
            dict: A JSON object containing the email information.
        """
        warnings.warn(
            "get_email_info() is deprecated, use get_messages() or get_mailboxes() instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return self.get_messages(path, length, start, order, dir)

    def get_email_source(self, uid, path="INBOX"):
        """
        Retrieves the source code of an email message from the specified email path and message ID.

        Args:
            uid (int): The unique identifier of the email message.
            path (str, optional): The path of the email folder. Defaults to "INBOX".

        Returns:
            str: The source code of the email message.
        """
        email_source = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/mail/show/source?path={path}&msg={str(uid)}"
        ).text
        logging.info("Got Email source")
        return email_source

    def get_mail_folders(self):
        """
        Retrieves the list of mail folders.

        Deprecated:
            `/iserv/mail/api/folder/list` no longer returns JSON on current IServ versions.
            This now returns the result of `get_mailboxes()`, use that method directly instead.

        :return: A JSON object containing the list of mail folders.
        """
        warnings.warn(
            "get_mail_folders() is deprecated, use get_mailboxes() instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        return self.get_mailboxes()

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

        # Create a message
        if attachments != None:
            if type(attachments) != list and attachments:
                logging.error("Attachments must be list!")
                raise TypeError("Attachments must be list!")

        if smtp_server == None:
            smtp_server = self.api.iserv_url

        message = MIMEMultipart()
        message["From"] = f"{self.api.username}@{self.api.iserv_url}"
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach plain text body
        message.attach(MIMEText(body, "plain"))

        if html_body:
            # Attach HTML body
            message.attach(MIMEText(html_body, "html"))

        if attachments:
            for attachment in attachments:
                # Open the file in binary mode
                with open(attachment, "rb") as file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file.read())
                # Encode the file data into base64
                encoders.encode_base64(part)
                # Set the filename parameter
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(attachment)}"',
                )
                # Add attachment to the message
                message.attach(part)
                logging.debug(attachment)

        # Connect to SMTP server using SMTPS port
        with smtplib.SMTP_SSL(smtp_server, smtps_port) as server_ssl:
            server_ssl.login(self.api.username, self.api._password)
            server_ssl.sendmail(
                self.api.username + "@" + self.api.iserv_url,
                receiver_email,
                message.as_string(),
            )
            logging.info(
                "Email sent successfully via SMTPS (port {}).".format(smtps_port)
            )
