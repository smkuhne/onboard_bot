import discord
import json
import sqlite3

from modules.scheduling import scheduling
from modules.administration import setup, help
from modules.survey import survey

client = discord.Client()
conn = sqlite3.connect('database/events.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Guilds(id INT NOT NULL PRIMARY KEY, gid TEXT, daily INT, weekly INT, yearly INT)''')
mscheduler = scheduling(client, cursor)
token_bot = ''

with open('tokens.json') as token_file:
    data = json.load(token_file)
    token_bot = data['bot']

scheduler_commands = {
    'events': mscheduler.events,
    'create': mscheduler.create,
    'edit': mscheduler.edit,
    'remove': mscheduler.remove,
}

subscription_commands = {
    'subscribe': mscheduler.subscribe,
    'unsubscribe': mscheduler.unsubscribe
}

other_commands = {
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
 
        if str_arr[1] in scheduler_commands:
            if message.author.guild_permissions.administrator:
                await scheduler_commands[str_arr[1]](message, str_arr[2:])
        elif str_arr[1] in subscription_commands:
            await subscription_commands[str_arr[1]](message, str_arr[2:])
        elif str_arr[1] in other_commands:
            await other_commands[str_arr[1]](message, str_arr[2:])
        else:
            await other_commands['help'](message, str_arr)

    conn.commit()

client.run(token_bot)