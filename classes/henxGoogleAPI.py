#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import sys
import time
import xml.etree.ElementTree as ET


class HenxGoogleAPIClass:
    """ Class for working with the Google Contacts and the OAuth API
        OAuth 2.0 for limited input devices: https://developers.google.com/identity/protocols/OAuth2ForDevices
        Contacts API 3.0: https://developers.google.com/google-apps/contacts/v3/
    """

    def __init__(self, sql_object):
        """ class initialization
        :param sql_object: instant of the HenxSQLiteClass
        """
        self.sql = sql_object

    def _obtain_user_code(self):
        """ Getting the user_code by using the client_id and client_secret
                https://developers.google.com/identity/protocols/OAuth2ForDevices#obtainingacode
        :return: 1 if anything with the request went wrong
                JSON Object with the interval and the device_code if everything went right
                    {"interval":data, "device_code":data}
        """
        url = self.sql.get_parameter("obtain_user_code_url")
        payload = {"client_id": self.sql.get_parameter("client_id"),
                   "scope": self.sql.get_parameter("scope")}
        r = requests.post(url, data=payload)

        # Debug
        # print(r.text)

        # Abfrage bzgl. response code einfügen
        response = r.json()
        if "Error" in response:
            print("Error: " + response["Error"])
            return 1
        else:
            print("Verification URL: " + response["verification_url"])
            print("User Code: " + response["user_code"])
            print("Expires in: " + str((response["expires_in"] / 60)) + " Min")
            # Debug
            # print("Device code: " + response["device_code"])
            # self.xml.write_xml("device_code", response["device_code"])
            self.sql.update_parameter("device_code", response["device_code"])

        return {"interval": response["interval"], "device_code": response["device_code"]}

    def _obtain_initial_tokens(self):
        """ Getting the refresh_token and the first access_token for using the API
                https://developers.google.com/identity/protocols/OAuth2ForDevices#obtainingatoken
            Writes the tokens into the config DB
        :return: 0 if everything went right
                 1 of anything went wrong
        """
        url = self.sql.get_parameter("obtain_token_url")
        payload = {"client_id": self.sql.get_parameter("client_id"),
                   "client_secret": self.sql.get_parameter("client_secret"),
                   "code": self.sql.get_parameter("device_code"),
                   "grant_type": self.sql.get_parameter("grant_type")}
        r = requests.post(url, data=payload)
        # Debug
        # print(r.text)
        response = r.json()

        if "refresh_token" in response:
            self.sql.update_parameter("access_token", response["access_token"])
            self.sql.update_parameter("refresh_token", response["refresh_token"])
            # self.xml.write_xml("token_type", "Bearer")
            return 0
        elif "Error" in response:
            print("Error: " + response["error"])
            return 1
        else:
            return 1

    def _obtain_new_access_token(self):
        """ Gets a new access_token using the refresh_token in case the access_token expires.
                https://developers.google.com/identity/protocols/OAuth2ForDevices#refreshtoken
            Writes the new tokens into the config DB
        :return: 0 if everything went right
                 1 if anything went wrong
        """
        url = self.sql.get_parameter("obtain_token_url")
        payload = {"client_id": self.sql.get_parameter("client_id"),
                   "client_secret": self.sql.get_parameter("client_secret"),
                   "refresh_token": self.sql.get_parameter("refresh_token"),
                   "grant_type": "refresh_token"}
        r = requests.post(url, data=payload)
        # Debug
        # print(r.text)
        response = r.json()

        if "access_token" in response:
            self.sql.update_parameter("access_token", response["access_token"])
            return 0
        else:
            return 1

    def _input_api_data(self):
        """ Asking the user to input client_id and client_secret from the Google API Console
            If user presses Ctrl+C it stops the script
        :return: nothing
        """
        # client_id = self.xml.get_xml("client_id")
        client_id = self.sql.get_parameter("client_id")
        if client_id is None:
            try:
                client_id = input("Input Google API client ID: ")
                # self.xml.write_xml("client_id", client_id)
                self.sql.update_parameter("client_id", client_id)
            except KeyboardInterrupt:
                sys.exit(1)

        # client_secret = self.xml.get_xml("client_secret")
        client_secret = self.sql.get_parameter("client_secret")
        if client_secret is None:
            try:
                client_secret = input("Input Google API client secret: ")
                # self.xml.write_xml("client_secret", client_secret)
                self.sql.update_parameter("client_secret", client_secret)
            except KeyboardInterrupt:
                sys.exit(1)

    def delete_refresh_token(self):
        """ Debugging function for deleting refresh_token, access_token and device_code in the config DB
        :return: nothing
        """
        # self.xml.write_xml("refresh_token", "")
        # self.xml.write_xml("access_token", "")
        # self.xml.write_xml("device_code", "")
        self.sql.update_parameter("refresh_token", None)
        self.sql.update_parameter("access_token", None)
        self.sql.update_parameter("device_code", None)

    def delete_api_data(self):
        """ Debugging function for deleting client_id and client_secret in the config DB
        :return: nothing
        """
        # self.xml.write_xml("client_id", "")
        # self.xml.write_xml("client_secret", "")
        self.sql.update_parameter("client_id", None)
        self.sql.update_parameter("client_secret", None)

    def init_google_api(self):
        """ Initialization of the Google API and the config DB
            Asks the user for the Client-ID and the Client-Secret from the Google API console site if it's not there:
                https://console.developers.google.com/projectselector/apis/credentials
            After that the user needs to input the user code
                https://developers.google.com/identity/protocols/OAuth2ForDevices#displayingthecode
        :return: nothing
        """
        global user_code
        # self.xml.create_xml()
        self.sql.init_db()

        self._input_api_data()

        # debug = self.xml.get_xml("device_code")
        # if self.xml.get_xml("device_code") == 1 or self.xml.get_xml("device_code") is None:
        if self.sql.get_parameter("device_code") is None:
            user_code = self._obtain_user_code()
        elif self.sql.get_parameter("refresh_token") is None:
            user_code = self._obtain_user_code()

        while self.sql.get_parameter("refresh_token") is None:
            self._obtain_initial_tokens()
            print("Waiting for input of user code...")
            # print("There's something wrong with your API data. Please reenter:")
            # self.delete_API_data()
            # self.input_API_data()
            if "interval" in user_code:
                # self.obtain_initial_tokens()
                time.sleep(user_code["interval"])

    def get_all_contacts(self):
        """ Getting all contacts
        :return: unprocessed xml string from the Google API
        """
        url = "https://www.google.com/m8/feeds/contacts/[your email here]/full"
        header = {'GData-Version': '3.0'}
        payload = {"access_token": self.sql.get_parameter("access_token"),
                   "max-results": "5000"}
        r = requests.get(url, params=payload, headers=header)

        # if access token is expired (401 header reply), get new one
        if r.status_code == 401:
            self._obtain_new_access_token()
            r = requests.get(url, params=payload, headers=header)
        # Debug
        # print(r.text)
        return r.text

    def make_contact_array(self, xml_string):
        """ Processing the xml string from the API to a simple array containing just the name and the number of
            the contact
        :param xml_string: unprocessed xml string from the Google API
        :return: array with name and number of the contact:
                    [n][0]: name
                    [n][1]: number
        """
        global contact_id
        global name
        global contact_array
        global i
        contact_array = []

        # testinput vom file
        # tree = ET.parse("contacts_testdaten.xml")
        parser = ET.XMLParser(encoding='utf-8')
        tree = ET.fromstring(xml_string, parser=parser)

        for entry in tree.findall('{http://www.w3.org/2005/Atom}entry'):
            name = ""
            # contact_id = ""
            for child in entry.iter():
                # Debug
                # print (child.tag)
                # if child.tag == "{http://www.w3.org/2005/Atom}id":
                #     # Debug
                #     # print(child.text)
                #     contact_id = child.text

                if child.tag == "{http://www.w3.org/2005/Atom}title":
                    # Debug
                    # print(child.text)
                    name = child.text

                if child.tag == "{http://schemas.google.com/g/2005}phoneNumber" and name != "":
                    # Debug
                    # print(child.text)
                    # contact_array.append([name, child.text, contact_id])
                    contact_array.append([name, child.text])
        # Debug
        # print(contact_array)

        return contact_array

if __name__ == "__main__":
    exit()
