import discord
import sqlite3

from modules.scheduling import scheduling
from modules.administration import administration
from variables import token, zone

client = discord.Client()
conn = sqlite3.connect('database/events.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Guilds(id INT NOT NULL PRIMARY KEY, gid TEXT, timezone TEXT)''')
scheduler = scheduling(client, cursor, zone)
administrator = administration(client, cursor)

scheduler_commands = {
    'create': scheduler.create,
    'edit': scheduler.edit,
    'remove': scheduler.remove,
    'timezone': administrator.setup
}

subscription_commands = {
    'events': scheduler.events,
    'subscribe': scheduler.subscribe,
    'unsubscribe': scheduler.unsubscribe
}

other_commands = {
    'help': administrator.help
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

client.run(token)