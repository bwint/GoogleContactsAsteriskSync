
# GoogleContactsAsteriskSync #
#### Syncing your Google Contacts to a Asterisk phonebook for caller ID identification using *python3*. ####

Based on the idea I found [here](http://pbxinaflash.com/community/threads/google-contacts-to-asterisk-phonebook.10943/) I created a script to sync Google Contacts with an Asterisk phonebook for caller ID identification.

Because the original script is a few years old, it doesn’t cover the [OAuth 2.0 authentication mechanism](https://developers.google.com/identity/protocols/OAuth2) to access the Google API.
In my case I'm running a small Asterisk PBX a RaspberryPi. So I decided to use **[OAuth 2.0 for TV and Limited Input Device Applications](https://developers.google.com/identity/protocols/OAuth2ForDevices)**.

----------

## How to use it ##
*All Screenshots are in German, but I’m sure you’ll get the point.*

1. Activate the Contacts API in the [Google API console](https://console.developers.google.com/apis/library)
	 ![asdf](http://i.imgur.com/Zf9s2ku.jpg)
	 
2.  Create a project
	![enter image description here](http://i.imgur.com/3GSWvCZ.jpg)

3. Create a confirmation screen and an OAuth-Client-ID
	![enter image description here](http://i.imgur.com/rYyieZF.jpg)
	
	![enter image description here](http://i.imgur.com/BAFNIgp.jpg)

	![enter image description here](http://i.imgur.com/cx0wGLF.jpg)

4. Edit the ***GoogleContactsAsteriskSync.py*** file to suit your needs
	```python
	# Formatting the numbers
	county_code = "43"
	contact_array = format_numbers(contact_array, county_code)
	```
    Change the *country_code* to yours.

    ```python
    # If the second argument is set the script will send the Asterrisk commands to the print console instead of the system console
    asterisk_input(contact_array, True)
    ```
    Change it to *False* to execute the Asterisk commands.

    ```python
    contacts_array[i][1] = contact[1].replace(" ", "")
        contacts_array[i][1] = contact[1].replace("/", "")
        contacts_array[i][1] = contact[1].replace("+" + country_code, "0")
        contacts_array[i][1] = contact[1].replace("00" + country_code, "0")
        contacts_array[i][1] = contact[1].replace("+", "00")
        if contacts_array[i][0] == None:
            contacts_array[i][0] = "No Name"
    ```
    You can change the way the number is formatted in the *format_numbers* function.

5. Execute the script on your Asterisk machine