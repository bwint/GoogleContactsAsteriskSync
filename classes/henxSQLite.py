# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3


class HenxSQLiteClass:
    """ Class for creating and handling a sqlite DB for storing all the configuration.
        Database schema:
            Parameter CHAR(255) NOT NULL
            Value CHAR(255) NULL
        The following parameters exist:
            "client_id", "client_secret", "obtain_user_code_url", "obtain_token_url", "grant_type", "scope",
            "device_code", "access_token", "refresh_token"

        To-Do: Use constants for not changing parameters instead of the DB for simplification an speed.
    """

    # Name of the DB table
    TABLE = "config_table"

    def __init__(self, db_location):
        """
        :param db_location: Full path to sqlite DB file
        """
        self.db = db_location

    def _connect(self):
        """ Connect to sqlite DB file
        :return: sqlite connection object
        """
        conn = sqlite3.connect(self.db)
        return conn

    def _disconnect(self, connection):
        """ Disconnect from sqlite DB file
        :param connection: sqlite connection object
        :return: nothing
        """
        connection.close()

    def _sql_command_no_return(self, connection, sql_command):
        """ Exexutes a SQL command without a return (i.e. INSERT, UPDATE, etc.)
        :param connection: sqlite connection object
        :param sql_command: SQL command string
        :return: nothing
        """
        cursor = connection.cursor()
        cursor.execute(sql_command)
        connection.commit()
        cursor.close()

    def _row_exists(self, connection, parameter):
        """ Checks if a row with a given parameter exists or not.
        :param connection: sqlite connection object
        :param parameter: the parameter you want to look for
        :return: 1 if parameter exists, 0 if not, FALSE if anything with the query went wrong
        """
        cursor = connection.cursor()
        sql_command = "SELECT EXISTS(SELECT 1 FROM " + self.TABLE + " WHERE Parameter=\"" + parameter + "\" LIMIT 1);"
        cursor.execute(sql_command)
        result = cursor.fetchone()
        cursor.close()
        if len(result) >= 1:
            return result[0]
        else:
            return False

    def update_parameter(self, parameter, value):
        """ Updates a specific row in the DB with a given search parameter and value
            Because I use the DB just for storing the config there's always just one parameter with a specific name.
        :param parameter: search parameter for the "Parameter" column
        :param value: the value for the parameter
        :return: nothing
        """
        connection = self._connect()
        cursor = connection.cursor()
        sql_command = ("UPDATE " + self.TABLE + " "
                        "SET Value=\"" + value + "\""
                        "WHERE Parameter =\"" + parameter + "\";")
        cursor.execute(sql_command)
        connection.commit()
        cursor.close()
        self._disconnect(connection)

    def get_parameter(self, parameter):
        """ Get the value for a a specific parameter in the "Parameter" column.
            Because I use the DB just for storing the config there's always just one parameter with a specific name.
        :param parameter: the parameter you want to read the value for.
        :return: The Value of the parameter or FALSE if there wasn't one with the given parameter.
        """
        connection = self._connect()
        cursor = connection.cursor()
        sql_command = "SELECT Value FROM " + self.TABLE + " WHERE Parameter=\"" + parameter + "\" LIMIT 1;"
        cursor.execute(sql_command)
        result = cursor.fetchone()
        cursor.close()
        self._disconnect(connection)
        if len(result) >= 1:
            return result[0]
        else:
            return False

    def init_db(self):
        """ Initialization of the sqlite config DB.
            All URLs taken from the Google OAuth documentation for the use with limited input devices
             https://developers.google.com/identity/protocols/OAuth2ForDevices
        :return: nothing
        """
        conn = self._connect()
        # self.sql_command_no_return(conn, "CREATE DATABASE config_db;")
        sql_command = ("CREATE TABLE if not exists " + self.TABLE + " ("
                       #  "ID INT PRIMARY KEY  AUTOINCREMENT, "
                        "Parameter CHAR(255) NOT NULL, "
                        "Value CHAR(255) NULL"
                        ");")
        self._sql_command_no_return(conn, sql_command)
        parameters = ["client_id", "client_secret", "obtain_user_code_url", "obtain_token_url", "grant_type",
                      "scope", "device_code", "access_token", "refresh_token"]
        for parameter in parameters:
            if self._row_exists(conn, parameter) == 0:
                sql_command = ("INSERT INTO " + self.TABLE + " "
                                "(Parameter) "
                                "VALUES (\"" + parameter + "\")")
                self._sql_command_no_return(conn, sql_command)
        self.update_parameter("obtain_user_code_url", "https://accounts.google.com/o/oauth2/device/code")
        self.update_parameter("obtain_token_url", "https://www.googleapis.com/oauth2/v4/token")
        self.update_parameter("grant_type", "http://oauth.net/grant_type/device/1.0")
        self.update_parameter("scope", "https://www.google.com/m8/feeds")
        self._disconnect(conn)
