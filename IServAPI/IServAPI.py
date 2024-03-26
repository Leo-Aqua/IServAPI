import requests
import logging
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from lxml import etree
import urllib.parse
import webdav.client as wc
from webdav.exceptions import WebDavException



class IServAPI:
    def __init__(self, username, password, iserv_url):
        """
        Initializes the credentials and URLs needed for accessing the IServ system.

        :param username: str - The username for the IServ system.
        :param password: str - The password for the IServ system.
        :param iserv_url: str - The URL of the IServ system.
        :return: None
        """
        self.username = username
        self.password = password
        self.iserv_url = iserv_url
        self.session = None
        self.IServSAT = None
        self.IServSATId = None
        self.IServSession = None
        self.__DAVclient = None
        self.__login()

    def setup_logging(self, log_file="app.log"):
        """
        Set up a logger with a rotating file handler.
        
        This function initializes a logger that writes logs to a specified file. It uses
        a rotating file handler to limit the size of each log file to 1 MB and retains
        up to 5 backup copies of the log files.
        
        Args:
            log_file (str): The path to the log file.
        """
        
        # Initialize the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # Define the format for log messages
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=5  # Set file size to 1MB and keep 5 backups
        )
        file_handler.setLevel(logging.DEBUG)  # Log all DEBUG and higher level messages
        file_handler.setFormatter(formatter)  # Apply the formatter to the file handler
        
        # Attach the file handler to the logger
        logger.addHandler(file_handler)
        
        # Log a message indicating that logging was set up successfully
        logging.info("Logging setup successful!")
    
    def __get_cookies(self):
        # Create a session object to persist cookies across requests
        session = requests.Session()

        # First request to login page
        login_url = f'https://{self.iserv_url}/iserv/auth/login'
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }

        response = session.get(login_url, headers=headers)

        # Second request to submit login credentials
        login_data = {
            '_username': self.username,
            '_password': self.password
        }

        response = session.post(login_url, headers=headers, data=login_data)

        # Third request to home page
        home_url = f'https://{self.iserv_url}/iserv/auth/home'
        response = session.get(home_url, headers=headers)

        # Fourth request to main page
        main_page_url = f'https://{self.iserv_url}/iserv/'
        response = session.get(main_page_url, headers=headers)

        # Fifth request to main page again to get dynamic cookies
        response = session.get(main_page_url, headers=headers)

        # Print out the cookies
        cookies = session.cookies.get_dict()
        self.IServSAT = cookies.get("IServSAT")
        self.IServSATId = cookies.get("IServSATId")
        self.IServSession = cookies.get("IServSession")
        logging.info("Cookies extracted successfully!")
        return
    def __login(self):
        """
        Authenticates the user against the IServ server and initiates a session.

        This method performs a POST request with the user's credentials to the
        IServ authentication URL and checks for common failure scenarios such as
        non-existent accounts or failed login attempts due to wrong credentials.
        Upon successful login, it retrieves session cookies.

        Raises:
            ValueError: If the account does not exist or the login fails.
            ConnectionError: If there is a problem establishing a connection.
        """
        self.session = requests.Session()

        try:
            # Perform initial GET request to obtain login page and CSRF tokens if present
            base_response = self.session.get(f"https://{self.iserv_url}/iserv/auth/login")

            # Prepare login credentials to send with POST request
            login_data = {'_username': self.username, '_password': self.password}

            # Submit login credentials and check response
            login_response = self.session.post(base_response.url, data=login_data)

            # Check if the account does not exist
            if "Account existiert nicht!" in login_response.text:
                raise ValueError("Account does not exist!")

            # Check if the login has failed, usually due to incorrect credentials
            if "Anmeldung fehlgeschlagen!" in login_response.text:
                raise ValueError("Login failed! Probably wrong password.")

        except requests.exceptions.ConnectionError as e:
            # Handle connection errors during the login process
            raise ConnectionError(f"Error establishing connection: {e}")

        # Retrieve and store session cookies after successful login
        self.__get_cookies()
    def get_own_user_info(self):
        """
        Retrieves the user information from the server.

        Returns:
            dict: A dictionary containing the user information, including the following keys:
                - Groups (dict): A dictionary mapping group names to group URLs.
                - Roles (list): A list of role names.
                - Rights (list): A list of right names.
                - Public_info (dict): A dictionary containing the public information, including the following keys:
                    - title (str): The user's title.
                    - company (str): The user's company.
                    - birthday (str): The user's birthday.
                    - nickname (str): The user's nickname.
                    - class (str): The user's class.
                    - street (str): The user's street address.
                    - zipcode (str): The user's zip code.
                    - city (str): The user's city.
                    - country (str): The user's country.
                    - icq (str): The user's ICQ number.
                    - jabber (str): The user's Jabber address.
                    - msn (str): The user's MSN address.
                    - skype (str): The user's Skype address.
                    - note (str): The user's note.
                    - phone (str): The user's phone number.
                    - mobilePhone (str): The user's mobile phone number.
                    - fax (str): The user's fax number.
                    - mail (str): The user's email address.
                    - homepage (str): The user's homepage URL.
                    - _token (str): The user's token.
        """
    
        if not self.session:
            raise ValueError("Session is not initialized. Please log in first.")
        try:
            user_info_response = self.session.get(f"https://{self.iserv_url}/iserv/profile")
            
        
        except Exception as e:
            logging.error(f"Error retrieving user information: {e}")
            raise ValueError("Error retrieving user information")
        user_info = {}
        try:
            personal_information_data_response = self.session.get(f"https://{self.iserv_url}/iserv/profile/public/edit#data")
            personal_information_adress_response = self.session.get(f"https://{self.iserv_url}/iserv/profile/public/edit#address")
            personal_information_contact_response = self.session.get(f"https://{self.iserv_url}/iserv/profile/public/edit#contact")
            personal_information_instant_response = self.session.get(f"https://{self.iserv_url}/iserv/profile/public/edit#instant")
            personal_information_note_response = self.session.get(f"https://{self.iserv_url}/iserv/profile/public/edit#note")
        except Exception as e:
            logging.error(f"Error retrieving user information: {e}")
            
        user_info_soup = BeautifulSoup(user_info_response.text, 'html.parser')
        root = etree.HTML(str(user_info_soup))
        

        # Groups
        xpath_expr = "/html/body/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/ul[1]"
        matching_elements = root.xpath(xpath_expr)
        matching_soup_elements = [BeautifulSoup(etree.tostring(elem), 'html.parser') for elem in matching_elements]
        
        groups_dict = {}
        for soup in matching_soup_elements:
            # Find the <a> tag
            ul_tag = soup.find('ul')
            a_tags = ul_tag.find_all('a')
            for a_tag in a_tags:
                text = a_tag.text
                href = a_tag['href']
                groups_dict[text] = href
    
        logging.info("Got Groups")

        # Roles
        xpath_expr = "/html/body/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/ul[2]"
        matching_elements = root.xpath(xpath_expr)
        matching_soup_elements = [BeautifulSoup(etree.tostring(elem), 'html.parser') for elem in matching_elements]
        roles_list = []
        for soup in matching_soup_elements:
            # Find the <a> tag
            ul_tag = soup.find('ul')
            li_tags = ul_tag.find_all('li')
            for li_tag in li_tags:
                text = li_tag.text
                
                roles_list.append(text)
    
        logging.info("Got Roles")
        

        # Rights
        xpath_expr = "/html/body/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/ul[3]"
        matching_elements = root.xpath(xpath_expr)
        matching_soup_elements = [BeautifulSoup(etree.tostring(elem), 'html.parser') for elem in matching_elements]
        rights_list = []
        for soup in matching_soup_elements:
            # Find the <a> tag
            ul_tag = soup.find('ul')
            li_tags = ul_tag.find_all('li')
            for li_tag in li_tags:
                text = li_tag.text
                
                rights_list.append(text)
    
        logging.info("Got Rights")
        
        

        # Public information:
        public_info_json = {}


        soup = BeautifulSoup(personal_information_data_response.text, "html.parser")


        ids_and_keys = [
            ("publiccontact_title", "title"),
            ("publiccontact_company", "company"),
            ("publiccontact_birthday", "birthday"),
            ("publiccontact_nickname", "nickname"),
            ("publiccontact_class", "class")
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ''

        soup = BeautifulSoup(personal_information_adress_response.text, "html.parser")
        
        ids_and_keys = [
            ("publiccontact_street", "street"),
            ("publiccontact_zipcode", "zipcode"),
            ("publiccontact_city", "city"),
            ("publiccontact_country", "country")
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ''


        soup = BeautifulSoup(personal_information_instant_response.text, "html.parser")
        ids_and_keys = [
            ("publiccontact_icq", "icq"),
            ("publiccontact_jabber", "jabber"),
            ("publiccontact_msn", "msn"),
            ("publiccontact_skype", "skype")
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ''

        soup = BeautifulSoup(personal_information_note_response.text, "html.parser")
        ids_and_keys = [
            ("publiccontact_note", "note")
        ]
        
        for id, key in ids_and_keys:
            
            try:
                value = soup.find("textarea", id=id).get_text()
                
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ''

        
        soup = BeautifulSoup(personal_information_contact_response.text, "html.parser")
        ids_and_keys = [
            ("publiccontact_phone", "phone"),
            ("publiccontact_mobilePhone", "mobilePhone"),
            ("publiccontact_fax", "fax"),
            ("publiccontact_mail", "mail"),
            ("publiccontact_homepage", "homepage")
        ]
        
        for id, key in ids_and_keys:
                try:
                    value = soup.find("input", id=id)["value"]
                    public_info_json[key] = value
                except KeyError:
                    logging.warning(f"No data in {id}")
                    public_info_json[key] = ''


        soup = BeautifulSoup(personal_information_contact_response.text, "html.parser")
        ids_and_keys = [
            ("publiccontact__token", "_token")
        ]
        
        for id, key in ids_and_keys:
                try:
                    value = soup.find("input", id=id)["value"]
                    public_info_json[key] = value
                except KeyError:
                    logging.warning(f"No data in {id}")
                    public_info_json[key] = ''

        logging.info("Got Public info")

        user_info["Groups"] = groups_dict
        user_info["Roles"] = roles_list
        user_info["Rights"] = rights_list
        user_info["Public_info"] = public_info_json
        return user_info

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

        if not self.session:
            raise ValueError("Session is not initialized. Please log in first.")
        try:
            

            def modify_data(userinfo, settings0):
                
                data = {
                    'publiccontact[title]': userinfo["Public_info"]["title"],
                    'publiccontact[company]': userinfo["Public_info"]["company"],
                    'publiccontact[birthday]': userinfo["Public_info"]["birthday"],
                    'publiccontact[nickname]': userinfo["Public_info"]["nickname"],
                    'publiccontact[class]': userinfo["Public_info"]["class"],
                    'publiccontact[street]': userinfo["Public_info"]["street"],
                    'publiccontact[zipcode]': userinfo["Public_info"]["zipcode"],
                    'publiccontact[city]': userinfo["Public_info"]["city"],
                    'publiccontact[country]': userinfo["Public_info"]["country"],
                    'publiccontact[phone]': userinfo["Public_info"]["phone"],
                    'publiccontact[mobilePhone]': userinfo["Public_info"]["mobilePhone"],
                    'publiccontact[fax]': userinfo["Public_info"]["fax"],
                    'publiccontact[mail]': userinfo["Public_info"]["mail"],
                    'publiccontact[homepage]': userinfo["Public_info"]["homepage"],
                    'publiccontact[icq]': userinfo["Public_info"]["icq"],
                    'publiccontact[jabber]': userinfo["Public_info"]["jabber"],
                    'publiccontact[msn]': userinfo["Public_info"]["msn"],
                    'publiccontact[skype]': userinfo["Public_info"]["skype"],
                    'publiccontact[note]': userinfo["Public_info"]["note"],
                    'publiccontact[hidden]': '0',
                    'publiccontact[actions][submit]': '',
                    'publiccontact[_token]': urllib.parse.quote(userinfo["Public_info"]["_token"])
                }

                # Update data with settings0
                for key, value in settings.items():
                    if key == 'title':
                        data['publiccontact[title]'] = value
                        logging.info("changed title to" + value)
                    elif key == 'company':
                        data['publiccontact[company]'] = value
                        logging.info("changed company to" + value)
                    elif key == 'birthday':
                        data['publiccontact[birthday]'] = value
                        logging.info("changed birthday to" + value)
                    elif key == 'nickname':
                        data['publiccontact[nickname]'] = value
                        logging.info("changed nickname to" + value)
                    elif key == '_class':
                        data['publiccontact[class]'] = value
                        logging.info("changed class to" + value)
                    elif key == 'street':
                        data['publiccontact[street]'] = value
                        logging.info("changed street to" + value)
                    elif key == 'zipcode':
                        data['publiccontact[zipcode]'] = value
                        logging.info("changed zipcode to" + value)
                    elif key == 'city':
                        data['publiccontact[city]'] = value
                        logging.info("changed city to" + value)
                    elif key == 'country':
                        data['publiccontact[country]'] = value
                        logging.info("changed country to" + value)
                    elif key == 'phone':
                        data['publiccontact[phone]'] = value
                        logging.info("changed phone to" + value)
                    elif key == 'mobilePhone':
                        data['publiccontact[mobilePhone]'] = value
                        logging.info("changed mobilePhone to" + value)
                    elif key == 'fax':
                        data['publiccontact[fax]'] = value
                        logging.info("changed fax to" + value)
                    elif key == 'mail':
                        data['publiccontact[mail]'] = value
                        logging.info("changed mail to" + value)
                    elif key == 'homepage':
                        data['publiccontact[homepage]'] = value
                        logging.info("changed homepage to" + value)
                    elif key == 'icq':
                        data['publiccontact[icq]'] = value
                        logging.info("changed icq to" + value)
                    elif key == 'jabber':
                        data['publiccontact[jabber]'] = value
                        logging.info("changed jabber to" + value)
                    elif key == 'msn':
                        data['publiccontact[msn]'] = value
                        logging.info("changed msn to" + value)
                    elif key == 'skype':
                        data['publiccontact[skype]'] = value
                        logging.info("changed skype to" + value)
                    elif key == 'note':
                        data['publiccontact[note]'] = value
                        logging.info("changed note to" + value)
                    

                return data
            
            userinfo = self.get_own_user_info()
            data = modify_data(userinfo, settings)
             
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'null',
                'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
              
            cookies = {
                "IServSAT" : self.IServSAT,
                "IServSATId" : self.IServSATId,
                "IServSession" : self.IServSession
            }
            response = requests.post(f"https://{self.iserv_url}/iserv/profile/public/edit", headers=headers, cookies=cookies, data=data, allow_redirects=True)
            logging.info("Public info changed successfully")
            return response.status_code
        except Exception as e:
            logging.error(f"Error setting user information: {e}")
            raise ValueError("Error setting user information")
    
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
        avatar = self.session.get(f"https://{self.iserv_url}/iserv/core/avatar/user/{user}")
        
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
        
    def get_emails(self, path = 'INBOX', length = 50, start = 0, order = 'date', dir = 'desc'):
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
        return self.session.get(f"https://{self.iserv_url}/iserv/mail/api/message/list?path={path}&length={str(length)}&start={str(start)}&order%5Bcolumn%5D={order}&order%5Bdir%5D={dir}").json()
    def search_users(self):
        """
        Search for users by making a GET request to the IServ address book lookup endpoint.

        :return: The JSON response containing the search results.
        """
        return "Not implemented yet! use search_users_autocomplete() instead!"
        return self.session.get(f"https://{self.iserv_url}iserv/addressbook/lookup").json()

    def search_users_autocomplete(self, query, limit=50):
        """
        Perform autocomplete search for users based on the query and optional limit.

        Args:
            query (str): The search query.
            limit (int, optional): The maximum number of results to return. Defaults to 50.

        Returns:
            dict: The JSON response containing the list of users matching the query.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/core/autocomplete/api?type=user,list&query={query}&limit={str(limit)}").json()
    
    def get_notifications(self):
        """
        Retrieves notifications from the specified URL and returns them as a JSON object.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/user/api/notifications").json()
    
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
        return self.session.get(f"https://{self.iserv_url}/iserv/mail/api/message/list?path={path}&length={str(length)}&start={str(start)}&order%5Bcolumn%5D={order}&order%5Bdir%5D={dir}").json()

    def get_email_source(self, uid, path="INBOX"):
        """
        Retrieves the source code of an email message from the specified email path and message ID.

        Args:
            uid (int): The unique identifier of the email message.
            path (str, optional): The path of the email folder. Defaults to "INBOX".

        Returns:
            str: The source code of the email message.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/mail/show/source?path={path}&msg={str(uid)}").text

    def get_mail_folders(self):
        """
        Retrieves the list of mail folders from the IServ API.

        :return: A JSON object containing the list of mail folders.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/mail/api/folder/list").json()
    
    def get_upcoming_events(self):
        """
        Retrieves the upcoming events from the IServ calendar API.

        :return: A JSON object containing the upcoming events.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/calendar/api/upcoming").json()

    def get_eventsources(self):
        """
        Retrieves the event sources from the calendar API.

        :return: A JSON object containing the event sources.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/calendar/api/eventsources").json()

    def get_conference_health(self):
        """
        Get the health status of the conference API endpoint.

        :return: JSON response containing the health status of the API
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/videoconference/api/health").json()
    
    def get_badges(self):
        """
        Retrieves the badges from the IServ server.

        :return: A JSON object containing the badges.
        """
        return self.session.get(f"https://{self.iserv_url}/iserv/app/navigation/badges").json()
    
    
    def file(self, davurl = "default", username="default", password="default", path="/"):
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
        try:
            davurl = "webdav."+self.iserv_url if davurl == "default" else davurl
            username = self.username if username == "default" else username
            password = self.password if password == "default" else password
            options = {
                'webdav_hostname': "https://"+ davurl,
                'webdav_login':    username,
                'webdav_password': password
                }
            self.__DAVclient = wc.Client(options)
            return self.__DAVclient
        except WebDavException as e:
            logging.error("Exception at file (webdav): " + str(e))
            raise ValueError("Exception at file (webdav): " + str(e))
    
    
    
 
        
if __name__ == "__main__":
    # Set up logging
    log_file = 'app.log'
    IServAPI.setup_logging(log_file)

    