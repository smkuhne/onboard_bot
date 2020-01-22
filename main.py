import discord
import json

from modules.event import event
from modules.survey import survey

client = discord.Client()
token_bot = ''
token_firebase = ''

event_dict = {}

with open('tokens.json') as token_file:
    data = json.load(token_file)
    token_bot = data['bot']
    token_firebase = data['firebase']

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # Don't react if the bot is the one writing the message
    if message.author == client.user:
        return

    # If event is to be created, then do so
    if message.content.startswith('$event'):
        event_dict[message.author.name + message.channel.name + message.guild.name] = event(message)
        success = await event_dict[message.author.name + message.channel.name + message.guild.name].create(message)

        if success == 0:
            await event_dict[message.author.name + message.channel.name + message.guild.name].error(message)
    
    elif (message.author.name + message.channel.name + message.guild.name) in event_dict:
        success = await event_dict[message.author.name + message.channel.name + message.guild.name].create(message)

        if success == 0:
            await event_dict[message.author.name + message.channel.name + message.guild.name].error(message)

        elif success == 2:
            del event_dict[message.author.name + message.channel.name + message.guild.name]
        

client.run(token_bot)