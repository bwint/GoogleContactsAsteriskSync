#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Syncing Google Contacts with the Asterisk phonebook with OAuth 2.0 authentification
# Idea: http://pbxinaflash.com/community/threads/google-contacts-to-asterisk-phonebook.10943/
# Author: Bernhard Wintersperger
# v 0.9

# Imports
import os
from classes import henxGoogleAPI
from classes import henxSQLite

# Getting the directory of this file
directory = os.path.dirname(os.path.abspath(__file__))

# Instantiating of the sqlite and the Google API class
sql = henxSQLite.HenxSQLiteClass(directory + "/config/config.db")
gAPI = henxGoogleAPI.HenxGoogleAPIClass(sql)


def asterisk_input(contact_array, *printtonly):
    """ Inputs the formatted contact array into Asterrisk or prints it to the console
        Because syncing the Asterrisk contacts is not possible all contacts get deleted and will be added again.
    :param contact_array: tho formatted contacts
                            [n][0]: name
                            [n][1]: number
    :param printtonly: if set the function will print the Asterrisk commands instead of executing it
    :return:
    """
    if printtonly:
        print("Only printing to python console:")
        print("asterisk -rx \'database deltree cidname\'")
        for contact in contact_array:
            print("asterisk -rx \'database put cidname %s \"%s\"\'" % (contact[1], contact[0]))
        input("Press Enter to exit\n")
    else:
        # Delete all of our contacts
        os.system("asterisk -rx \'database deltree cidname\'")
        for contact in contact_array:
            # Insert the number into the cidname database
            os.system("asterisk -rx \'database put cidname %s \"%s\"\'" % (contact[1], contact[0]))


def format_numbers(contacts_array, country_code):
    """ Cleaning the numbers in of the contact array
    I live in austria and my phone provider sends the caller id starting with a 0 and then the local or mobile code.
    So I clean all my entries to match that caller id format.
    :param contacts_array: the parsed and converted contact_array
                            [n][0]: name
                            [n][1]: number
    :param country_code: your country code; i.e.: Austria: 43, Germany: 49, etc.
    :return: the cleaned contact array
    """
    i = 0
    for contact in contacts_array:
        contacts_array[i][1] = contact[1].replace(" ", "")
        contacts_array[i][1] = contact[1].replace("/", "")
        contacts_array[i][1] = contact[1].replace("+" + country_code, "0")
        contacts_array[i][1] = contact[1].replace("00" + country_code, "0")
        contacts_array[i][1] = contact[1].replace("+", "00")
        if contacts_array[i][0] == None:
            contacts_array[i][0] = "No Name"
        i += 1
        # Debug
        # print(contact)
    return contacts_array


if __name__ == "__main__":
    # For debugging purposes
    # gAPI.delete_refresh_token()
    # gAPI.delete_api_data()

    print("##########################################")
    print("### Sync Google Contacts with Asterisk ###")
    print("##########################################\n")

    # Initialisation of the Google API
    gAPI.init_google_api()

    print("Getting Google Contacts data...")
    # Getting the raw contacts in XML format
    xml_contacts = gAPI.get_all_contacts()
    # XML parsing and formatting into an array
    contact_array = gAPI.make_contact_array(xml_contacts)

    # Formatting the numbers
    county_code = "44"
    contact_array = format_numbers(contact_array, county_code)

    print("Starting input to asterisk....")
    # If the second argument is set the script will send the Asterrisk commands to the print console instead
    # of the system console
    asterisk_input(contact_array)

    print("Done")
