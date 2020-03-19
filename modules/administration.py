class administration:
    def __init__(self, client, cursor):
        self.client = client
        self.cursor = cursor

    async def setup(self, message, chunks):
        if len(chunks) == 0:
            await message.channel.send('Usage: sudo timezone <timezone>\n' \
            'Where the timezone must be in the following UTC format +HHMM')
        
        try:
            self.cursor.execute('''UPDATE Guilds SET timezone='{0}' WHERE id='{1}';'''.format(chunks[0], message.guild.id))

            await message.channel.send('Guild timezone updated, any previously created events are locked in the original timezone, recreate them to adjust to the new timezone')
        except Exception as inst:
            print(inst)
            await message.channel.send('Guild timezone could not be updated')

    async def help(self, message, chunks):
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
            '-r <weekly, daily, none> specify how often you want the event to repeat\n' \
            '-c <channel> ping a channel to indicate which channel the announcement should be provided in' \
            'Edit an event that already exists on the server\n' \
            'Usage: sudo edit <title> [options]\n\n' \
            '-d <description> to set a description\n' \
            '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n' \
            '-a <location> indicate where the event will take place\n' \
            '-l <link> indicate a link to which members can refer for information about the event\n' \
            '-r <weekly, daily, none> specify how often you want the event to repeat\n' \
            '-c <channel> ping a channel to indicate which channel the announcement should be provided in' \
            'Remove an event from the server\n' \
            'Usage: sudo remove <title>\n\n\n' \
            'Subscribe to an event that exists on this server.\n' \
            'Usage: sudo subscribe <title>\n\n\n' \
            'Unsubsribe from an event on this server.\n' \
            'Usage: sudo unsubscribe <title>\n\n\n' \
            'Setup the server with a role and channel.\n' \
            'Usage: sudo timezone <timezone>\n\n' \
            'Where the timezone must be in the following UTC format +HHMM\n\n\n'
            'Show this message.\n' \
            'Usage: sudo help')
