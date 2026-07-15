from io import StringIO
import logging
import urllib.parse
from bs4 import BeautifulSoup
import pandas


class Users:
    def __init__(self, api) -> None:
        self.api = api

    def get_user_profile_picture(self, user, output_folder: str):
        """
        Retrieves the profile picture of a user and saves it to the specified output folder.

        This function checks if the user's avatar is in SVG format and saves it with the
        appropriate file extension, otherwise, it assumes the image is in WEBP format.

        Args:
            user (str): The username of the user whose profile picture is to be retrieved.
            output_folder (str): The directory path where the profile picture will be saved.

        """
        # Send a GET request to the URL that hosts the user's avatar
        avatar = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/core/avatar/user/{user}"
        )

        # Prepare the file path, replacing backslashes with forward slashes and removing trailing slashes
        file_path = output_folder.replace("\\", "/").removesuffix("/") + "/"

        # Check if the avatar is in SVG format
        if "<svg" in avatar.text:
            # If so, write the SVG content to a file with an SVG extension
            with open(file_path + user + ".svg", "w") as f:
                f.write(avatar.text)
        else:
            # If not, write the content to a file with a WEBP extension in binary mode
            with open(file_path + user + ".webp", "wb") as f:
                f.write(avatar.content)

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

        query = urllib.parse.quote(query)
        resonse = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/addressbook/public?filter%5Bsearch%5D={query}",
            allow_redirects=True,
        )
        soup = BeautifulSoup(resonse.text, "html.parser")

        if "Too many results, please restrict filter criteria!" in resonse.text:
            logging.error("Too many results, please restrict filter criteria!")
            raise ValueError("Too many results, please restrict filter criteria!")

        if "Zu viele Treffer, bitte Filterkriterien einschränken!" in resonse.text:
            logging.error("Too many results, please restrict filter criteria!")
            raise ValueError("Too many results, please restrict filter criteria!")

        else:
            table = str(soup.find("table").contents[3])

            soup = BeautifulSoup(table, "html.parser")

            rows = soup.find_all("tr")

            # Initialize an empty list to store dictionaries
            content_href_list = []

            # Extract the first <a> tag from each row and store in a dictionary
            for row in rows:
                # Find the first <a> tag within the row
                a_tag = row.find("a")
                # If an <a> tag is found, extract content and href attributes
                if a_tag:
                    content_href_dict = {
                        "name": a_tag.get_text(),
                        "user_url": a_tag.get("href"),
                    }
                    content_href_list.append(content_href_dict)
            logging.info("Searched users")
            return content_href_list

    def search_users_autocomplete(self, query, limit=50):
        """
        Perform autocomplete search for users based on the query and optional limit.

        Args:
            query (str): The search query.
            limit (int, optional): The maximum number of results to return. Defaults to 50.

        Returns:
            dict: The JSON response containing the list of users matching the query.
        """
        users = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/core/autocomplete/api?type=list,mail&query={query}&limit={str(limit)}"
        ).json()
        logging.info("Searched users (autocomplete)")
        return users

    def get_user_info(self, user):
        """
        A function to retrieve user information from a given URL and parse it into a dictionary.
        :param user: str - The user for who the information is being retrieved.
        :return: dict - A dictionary containing the user information.
        """
        response = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/addressbook/public/show/{user}"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if pd is None:
            raise ImportError("pandas is required for get_user_info")

        # Read the table into a list of DataFrames
        try:
            dfs = pandas.read_html(StringIO(str(table)), flavor="bs4")
            data = []
            for df in dfs:
                data_dict = dict(zip(df[0], df[1]))
                data.append(data_dict)
            logging.info("Got info of user " + user)
        except ValueError:
            logging.error("No such user found!")
            raise ValueError("No such user found!")

        return data[0]
