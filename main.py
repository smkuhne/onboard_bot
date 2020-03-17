import discord
import json
import sqlite3

from modules.master_scheduler import master_scheduler
from modules.event import subscribe, unsubscribe, help
from modules.survey import survey

mscheduler = master_scheduler()
client = discord.Client()
conn = sqlite3.connect('database/events.db')
c = conn.cursor()
token_bot = ''

with open('tokens.json') as token_file:
    data = json.load(token_file)
    token_bot = data['bot']

commands = {
    'events': mscheduler.events,
    'create': mscheduler.create,
    'edit': mscheduler.edit,
    'remove': mscheduler.remove,
    'subscribe': subscribe,
    'unsubscribe': unsubscribe,
    'help': help
}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # Don't react if the bot is the one writing the message
    if message.author == client.user:
        return

    # If event is to be created, then do so
    if message.content.startswith('sudo'):
        str_arr = message.content.split(' ')

        if str_arr[1] in commands:
            await commands[str_arr[1]](message, str_arr, c)
        else:
            await commands['help'](message, str_arr, c)

client.run(token_bot)