# Bot code

## Bot modules

## Socialbot.py

This module is the main module. It iniates bot integration with Webex Teams calls Webserver functions and keep waiting for Webex Webhooks.
Whenever a Webhook arrives, bot calls logica.py module to analyse user commands.

## Webexteams.py

This module has Webex Teams functions, such as Send Message to a Room, decrypt messages, etc.

## Webexteams_console_tools.py

A Console tool to test you bot before make it on production. It has also extra functions to test your bot (list of webhooks, list or rooms, etc).

## config.py

Config varibles module. This one gets the Webex Teams variables (url, tag, token, email) from config_shared. Also uses to load config.json file wich stores pairs of room:max occupation.

## logica.py

Main logic code. Understand user commands and executes it.
Treats POST from other modules to deliver messages to the users.

## construct.py

CLI code tool to generate user options.json file. The options are the commands that logic mode will load to present and understand commands available to the user, as well as the code identifier in order for logic module to execute appropiate functions.
