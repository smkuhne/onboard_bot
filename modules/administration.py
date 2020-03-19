import re
import os
import json
from pathlib import Path

async def setup(message, csplit):
    await message.channel.send('Changes successfully updated!')

async def help(message, csplit):
    await message.channel.send(' === These are the command onboard bot currently supports === \n' \
        'Look at the list of currently created events on the server.\n' \
        'Usage: sudo events\n\n\n' \
        'Create a new event for the server.\n' \
        'Usage: sudo create <title> [options]\n\n' \
        'Where options include:\n\n' \
        '-d <description> to set a description\n' \
        '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n' \
        '-a <location> indicate where the event will take place\n' \
        '-l <link> indicate a link to which members can refer for information about the event\n' \
        '-r <yearly, weekly, daily> specify how often you want the event to repeat\n' \
        '-c <channel> ping a channel to indicate which channel the announcement should be provided in' \
        'Edit an event that already exists on the server\n' \
        'Usage: sudo edit <title> [options]\n\n' \
        '-d <description> to set a description\n' \
        '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n' \
        '-a <location> indicate where the event will take place\n' \
        '-l <link> indicate a link to which members can refer for information about the event\n' \
        '-r <yearly, weekly, daily> specify how often you want the event to repeat\n' \
        '-c <channel> ping a channel to indicate which channel the announcement should be provided in' \
        'Remove an event from the server\n' \
        'Usage: sudo remove <title>\n\n\n' \
        'Subscribe to an event that exists on this server.\n' \
        'Usage: sudo subscribe <title>\n\n\n' \
        'Unsubsribe from an event on this server.\n' \
        'Usage: sudo unsubscribe <title>\n\n\n' \
        'Setup the server with a role and channel.\n' \
        'Usage: sudo setup [options]\n\n' \
        'Where options include:\n\n' \
        '-r <role> role which may create and edit events\n' \
        '-c <channel> channel all bot commands must be issued \n' \
        'Show this message.\n' \
        'Usage: sudo help')
