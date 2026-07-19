from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import os
import smtplib

from bs4 import BeautifulSoup


class Emails:
    def __init__(self, api) -> None:
        self.api = api

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

        Args:
            path (str, optional): The path in the mailbox to retrieve email information from. Defaults to "INBOX".
            length (int, optional): The number of email messages to retrieve. Defaults to 0 (retrieve all messages).
            start (int, optional): The index of the first email message to retrieve. Defaults to 0.
            order (str, optional): The column to order the email messages by. Defaults to "date".
            dir (str, optional): The direction of the ordering. Defaults to "desc" (descending).

        Returns:
            dict: A JSON object containing the email information.

        """
        email_info = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/mail/api/message/list?path={path}&length={str(length)}&start={str(start)}&order%5Bcolumn%5D={order}&order%5Bdir%5D={dir}"
        ).json()
        logging.info("Got Email info!")
        return email_info

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
        Retrieves the list of mail folders from the IServ API.

        :return: A JSON object containing the list of mail folders.
        """
        mail_folders = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/mail/api/folder/list"
        ).json()
        logging.info("Got Email Folders")
        return mail_folders

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
