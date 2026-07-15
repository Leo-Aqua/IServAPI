import logging
from bs4 import BeautifulSoup
from lxml import etree
from urllib import parse


class Profile:

    def __init__(self, api):
        self.api = api

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

        if not self.api._session:
            raise ValueError("Session is not initialized. Please log in first.")
        try:
            user_info_response = self.api._session.get(
                f"https://{self.api.iserv_url}/iserv/profile"
            )

        except Exception as e:
            logging.error(f"Error retrieving user information: {e}")
            raise ValueError("Error retrieving user information")
        user_info = {}
        try:
            personal_information_data_response = self.api._session.get(
                f"https://{self.api.iserv_url}/iserv/profile/public/edit#data"
            )
            personal_information_address_response = self.api._session.get(
                f"https://{self.api.iserv_url}/iserv/profile/public/edit#address"
            )
            personal_information_contact_response = self.api._session.get(
                f"https://{self.api.iserv_url}/iserv/profile/public/edit#contact"
            )
            personal_information_instant_response = self.api._session.get(
                f"https://{self.api.iserv_url}/iserv/profile/public/edit#instant"
            )
            personal_information_note_response = self.api._session.get(
                f"https://{self.api.iserv_url}/iserv/profile/public/edit#note"
            )
        except Exception as e:
            logging.error(f"Error retrieving user information: {e}")

        user_info_soup = BeautifulSoup(user_info_response.text, "html.parser")
        root = etree.HTML(str(user_info_soup))

        # Groups
        xpath_expr = "/html/body/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/ul[1]"
        matching_elements = root.xpath(xpath_expr)
        matching_soup_elements = [
            BeautifulSoup(etree.tostring(elem), "html.parser")
            for elem in matching_elements
        ]

        groups_dict = {}
        for soup in matching_soup_elements:
            # Find the <a> tag
            ul_tag = soup.find("ul")
            a_tags = ul_tag.find_all("a")
            for a_tag in a_tags:
                text = a_tag.text
                href = a_tag["href"]
                groups_dict[text] = href

        logging.info("Got Groups")

        # Roles
        xpath_expr = "/html/body/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/ul[2]"
        matching_elements = root.xpath(xpath_expr)
        matching_soup_elements = [
            BeautifulSoup(etree.tostring(elem), "html.parser")
            for elem in matching_elements
        ]
        roles_list = []
        for soup in matching_soup_elements:
            # Find the <a> tag
            ul_tag = soup.find("ul")
            li_tags = ul_tag.find_all("li")
            for li_tag in li_tags:
                text = li_tag.text

                roles_list.append(text)

        logging.info("Got Roles")

        # Rights
        xpath_expr = "/html/body/div/div[2]/div[3]/div/div/div[2]/div/div/div/div/ul[3]"
        matching_elements = root.xpath(xpath_expr)
        matching_soup_elements = [
            BeautifulSoup(etree.tostring(elem), "html.parser")
            for elem in matching_elements
        ]
        rights_list = []
        for soup in matching_soup_elements:
            # Find the <a> tag
            ul_tag = soup.find("ul")
            li_tags = ul_tag.find_all("li")
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
            ("publiccontact_class", "class"),
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ""

        soup = BeautifulSoup(personal_information_address_response.text, "html.parser")

        ids_and_keys = [
            ("publiccontact_street", "street"),
            ("publiccontact_zipcode", "zipcode"),
            ("publiccontact_city", "city"),
            ("publiccontact_country", "country"),
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ""

        soup = BeautifulSoup(personal_information_instant_response.text, "html.parser")
        ids_and_keys = [
            ("publiccontact_icq", "icq"),
            ("publiccontact_jabber", "jabber"),
            ("publiccontact_msn", "msn"),
            ("publiccontact_skype", "skype"),
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ""

        soup = BeautifulSoup(personal_information_note_response.text, "html.parser")
        ids_and_keys = [("publiccontact_note", "note")]

        for id, key in ids_and_keys:

            try:
                value = soup.find("textarea", id=id).get_text()

                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ""

        soup = BeautifulSoup(personal_information_contact_response.text, "html.parser")
        ids_and_keys = [
            ("publiccontact_phone", "phone"),
            ("publiccontact_mobilePhone", "mobilePhone"),
            ("publiccontact_fax", "fax"),
            ("publiccontact_mail", "mail"),
            ("publiccontact_homepage", "homepage"),
        ]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ""

        soup = BeautifulSoup(personal_information_contact_response.text, "html.parser")
        ids_and_keys = [("publiccontact__token", "_token")]

        for id, key in ids_and_keys:
            try:
                value = soup.find("input", id=id)["value"]
                public_info_json[key] = value
            except KeyError:
                logging.warning(f"No data in {id}")
                public_info_json[key] = ""

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

        if not self.api._session:
            raise ValueError("Session is not initialized. Please log in first.")
        try:

            def modify_data(userinfo, settings0):

                data = {
                    "publiccontact[title]": userinfo["Public_info"]["title"],
                    "publiccontact[company]": userinfo["Public_info"]["company"],
                    "publiccontact[birthday]": userinfo["Public_info"]["birthday"],
                    "publiccontact[nickname]": userinfo["Public_info"]["nickname"],
                    "publiccontact[class]": userinfo["Public_info"]["class"],
                    "publiccontact[street]": userinfo["Public_info"]["street"],
                    "publiccontact[zipcode]": userinfo["Public_info"]["zipcode"],
                    "publiccontact[city]": userinfo["Public_info"]["city"],
                    "publiccontact[country]": userinfo["Public_info"]["country"],
                    "publiccontact[phone]": userinfo["Public_info"]["phone"],
                    "publiccontact[mobilePhone]": userinfo["Public_info"][
                        "mobilePhone"
                    ],
                    "publiccontact[fax]": userinfo["Public_info"]["fax"],
                    "publiccontact[mail]": userinfo["Public_info"]["mail"],
                    "publiccontact[homepage]": userinfo["Public_info"]["homepage"],
                    "publiccontact[icq]": userinfo["Public_info"]["icq"],
                    "publiccontact[jabber]": userinfo["Public_info"]["jabber"],
                    "publiccontact[msn]": userinfo["Public_info"]["msn"],
                    "publiccontact[skype]": userinfo["Public_info"]["skype"],
                    "publiccontact[note]": userinfo["Public_info"]["note"],
                    "publiccontact[hidden]": "0",
                    "publiccontact[actions][submit]": "",
                    "publiccontact[_token]": parse.quote(
                        userinfo["Public_info"]["_token"]
                    ),
                }

                # Update data with settings0
                for key, value in settings.items():
                    if key == "title":
                        data["publiccontact[title]"] = value
                        logging.info("changed title to" + value)
                    elif key == "company":
                        data["publiccontact[company]"] = value
                        logging.info("changed company to" + value)
                    elif key == "birthday":
                        data["publiccontact[birthday]"] = value
                        logging.info("changed birthday to" + value)
                    elif key == "nickname":
                        data["publiccontact[nickname]"] = value
                        logging.info("changed nickname to" + value)
                    elif key == "_class":
                        data["publiccontact[class]"] = value
                        logging.info("changed class to" + value)
                    elif key == "street":
                        data["publiccontact[street]"] = value
                        logging.info("changed street to" + value)
                    elif key == "zipcode":
                        data["publiccontact[zipcode]"] = value
                        logging.info("changed zipcode to" + value)
                    elif key == "city":
                        data["publiccontact[city]"] = value
                        logging.info("changed city to" + value)
                    elif key == "country":
                        data["publiccontact[country]"] = value
                        logging.info("changed country to" + value)
                    elif key == "phone":
                        data["publiccontact[phone]"] = value
                        logging.info("changed phone to" + value)
                    elif key == "mobilePhone":
                        data["publiccontact[mobilePhone]"] = value
                        logging.info("changed mobilePhone to" + value)
                    elif key == "fax":
                        data["publiccontact[fax]"] = value
                        logging.info("changed fax to" + value)
                    elif key == "mail":
                        data["publiccontact[mail]"] = value
                        logging.info("changed mail to" + value)
                    elif key == "homepage":
                        data["publiccontact[homepage]"] = value
                        logging.info("changed homepage to" + value)
                    elif key == "icq":
                        data["publiccontact[icq]"] = value
                        logging.info("changed icq to" + value)
                    elif key == "jabber":
                        data["publiccontact[jabber]"] = value
                        logging.info("changed jabber to" + value)
                    elif key == "msn":
                        data["publiccontact[msn]"] = value
                        logging.info("changed msn to" + value)
                    elif key == "skype":
                        data["publiccontact[skype]"] = value
                        logging.info("changed skype to" + value)
                    elif key == "note":
                        data["publiccontact[note]"] = value
                        logging.info("changed note to" + value)

                return data

            userinfo = self.get_own_user_info()
            data = modify_data(userinfo, settings)

            response = self.api._session.post(
                f"https://{self.api.iserv_url}/iserv/profile/public/edit",
                data=data,
                allow_redirects=True,
            )
            logging.info("Public info changed successfully")
            return response.status_code
        except Exception as e:
            logging.error(f"Error setting user information: {e}")
            raise ValueError("Error setting user information")

    def get_groups(self) -> dict:

        groups = {}
        response = self.api._session.get(
            f"https://{self.api.iserv_url}/iserv/profile/grouprequest/add"
        )
        soup = BeautifulSoup(response.text, "html.parser")
        select = soup.find(
            "select",
            class_="select2",
        )
        options = select.children
        for option in options:
            groups[option.text] = option["value"]
        return groups
