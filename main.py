import discord
import json

client = discord.Client()
token_bot = ''
token_firebase = ''

with open('tokens.json') as token_file:
    data = json.load(token_file)
    token_bot = data['bot']
    token_firebase = data['firebase']

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$fun'):
        await message.channel.send('Letsa have some fun!')

client.run(token_bot)