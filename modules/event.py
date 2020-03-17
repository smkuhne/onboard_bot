import re
import os
import json
from pathlib import Path

async def subscribe(message, csplit, c):
    await message.channel.send('Subscribe to event')

async def unsubscribe(message, csplit, c):
    await message.channel.send('Unsubscribe from event')

async def setup(message, csplit, c):
    await message.channel.send('Changes successfully updated!')

async def help(message, csplit, c):
    await message.channel.send(' === These are the command onboard bot currently supports === \n' \
        'Look at the list of currently created events on the server.\n' \
        'Usage: sudo events\n\n\n' \
        'Create a new event for the server.\n' \
        'Usage: sudo create <title> [options]\n\n' \
        'Where options include:\n\n' \
        '-b <before> to indicate how many hours before a user should be notified\n' \
        '-d <description> to set a description\n' \
        '-r <days> number of days it takes to repeat\n' \
        '-s <date> indicating the day on which to start with format MM-DD-YYYY\n' \
        '-t <time> indicating what hour the event is taking place (1-24)\n\n\n' \
        'Edit an event that already exists on the server\n' \
        'Usage: sudo edit <title> [options]\n\n' \
        '-b <before> to indicate how many hours before a user should be notified\n' \
        '-d <description> to set a description\n' \
        '-r <days> number of days it takes to repeat\n' \
        '-s <date> indicating the day on which to start with format MM-DD-YYYY\n' \
        '-t <time> indicating what hour the event is taking place (1-24)\n\n\n' \
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
