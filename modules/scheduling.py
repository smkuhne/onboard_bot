import sqlite3
import time
from modules.dt import dt
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from datetime import timedelta

class scheduling:
    def __init__(self, client, cursor):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.client = client
        self.cursor = cursor

        self.cursor.execute('''SELECT * FROM Guilds''')

        rows = self.cursor.fetchall()

        for row in rows:
            self.cursor.execute('''SELECT * FROM {0}'''.format(row[1]))
            events = self.cursor.fetchall()
            
            self.cursor.execute('''SELECT * FROM Guilds WHERE id='{0}';'''.format(row[0]))
            guild = self.cursor.fetchone()

            for event in events:
                # Tell create the scheduler and tell the scheduler to send a message a certain time
                eventid = event[0]
                date = dt(ttype='string', string=event[3])
                repeat = event[4]
                if repeat == 'daily':
                    self.scheduler.add_job(self.notifier, 'interval', start_date=(date.datetime - timedelta(hours=int(guild[2]))), days=1, id=eventid, kwargs={'gid': guild[0],'eventid': eventid})
                elif repeat == 'weekly':
                    self.scheduler.add_job(self.notifier, 'interval', start_date=(date.datetime - timedelta(hours=int(guild[3]))), weeks=1, id=eventid, kwargs={'gid': guild[0],'eventid': eventid})
                elif repeat == 'yearly':
                    self.scheduler.add_job(self.notifier, 'interval', start_date=(date.datetime - timedelta(hours=int(guild[4]))), days=365, id=eventid, kwargs={'gid': guild[0],'eventid': eventid})

        print('Currently setting up all events again.')

    async def events(self, message, chunks):
        await message.channel.send('The following events where created on this server:')

        self.cursor.execute('''SELECT * FROM G_{0}'''.format(message.guild.id))
        rows = self.cursor.fetchall()

        for row in rows:
            await message.channel.send('"{0}"'.format(row[1]))

    ## Allows for the creation of a new recurring event
    async def create(self, message, chunks):

        # If the command is used incorrectly, tell the user what they are doing wrong
        if len(chunks) == 0:
            await message.channel.send('Usage: sudo create <title> [options]\n\n' \
            'Where options include:\n\n' \
            '-d <description> to set a description\n' \
            '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n' \
            '-a <location> indicate where the event will take place\n' \
            '-l <link> indicate a link to which members can refer for information about the event\n' \
            '-r <yearly, weekly, daily> specify how often you want the event to repeat\n' \
            '-c <channel> ping a channel to indicate which channel the announcement should be provided in')

            return
        
        # Don't crash the bot if something goes wrong
        try:
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)

            # Get information from the array of inputs
            description, date, location, link, repeat, channel = await self.parseOptions(chunks, message, ['N/A'], dt(ttype="time"), ['N/A'], 'N/A', 'weekly', message.channel.id)

            role = await message.guild.create_role(name='{0} Participants'.format(title), mentionable=True)
            # Add the data to a SQL table
            
            self.cursor.execute(''' SELECT * FROM Guilds WHERE id='{0}';'''.format(message.guild.id))
            row = self.cursor.fetchone()
            # Check if server has already been added to guilds
            if row is None:
                self.cursor.execute('''INSERT INTO Guilds VALUES ('{0}', 'G_{0}', '6', '24', '72')'''.format(message.guild.id))
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS G_{0}(id TEXT NOT NULL PRIMARY KEY, title TEXT, description TEXT, date TEXT, location TEXT, link TEXT, repeat TEXT, channel INT, role INT);'''.format(message.guild.id))
            self.cursor.execute('''INSERT INTO G_{0} VALUES ('{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}');'''.format(message.guild.id, eventid, title, description, str(date), location, link, repeat, channel, role.id))
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS `{0}`(member_id INT);'''.format(eventid))

            self.cursor.execute('''SELECT * FROM Guilds WHERE id='{0}';'''.format(message.guild.id))
            guild = self.cursor.fetchone()

            # Tell create the scheduler and tell the scheduler to send a message a certain time
            if repeat == 'daily':
                self.scheduler.add_job(self.notifier, 'interval', start_date=date.datetime - timedelta(hours=int(guild[2])), days=1, id=eventid, kwargs={'gid': message.guild.id,'eventid': eventid})
            elif repeat == 'weekly':
                self.scheduler.add_job(self.notifier, 'interval', start_date=date.datetime - timedelta(hours=int(guild[3])), weeks=1, id=eventid, kwargs={'gid': message.guild.id,'eventid': eventid})
            elif repeat == 'yearly':
                self.scheduler.add_job(self.notifier, 'interval', start_date=date.datetime - timedelta(hours=int(guild[4])), days=365, id=eventid, kwargs={'gid': message.guild.id,'eventid': eventid})

            # Confirm successfull creation of the event
            await message.channel.send('Your event {0}, has been created'.format(title))
        except Exception as inst:
            print(inst)
            await message.channel.send('There was an error creating your event, please retry.')
    
    async def edit(self, message, chunks):
        # If the command is used incorrectly, tell the user what they are doing wrong
        if len(chunks) == 0:
            await message.channel.send('Usage: sudo create <title> [options]\n\n' \
            'Where options include:\n\n' \
            '-d <description> to set a description\n' \
            '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n' \
            '-a <location> indicate where the event will take place\n' \
            '-l <link> indicate a link to which members can refer for information about the event\n' \
            '-r <yearly, weekly, daily> specify how often you want the event to repeat\n' \
            '-c <channel> ping a channel to indicate which channel the announcement should be provided in')

            return

        try:
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)
            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))

            row = self.cursor.fetchone()

            description, date, location, link, repeat, channel = await self.parseOptions(chunks, message, [row[2]], dt(ttype="string", string=row[3]), [row[4]], row[5], row[6], row[7])

            # Update the sqlite3 database
            self.cursor.execute('''UPDATE G_{0} SET description='{1}', date='{2}', location='{3}', link='{4}', repeat='{5}', channel='{6}' WHERE id='{7}';'''.format(message.guild.id, description, str(date), location, link, repeat, channel, eventid))

            if self.scheduler.get_job(eventid) is not None:
                self.scheduler.remove_job(eventid)

            self.cursor.execute('''SELECT * FROM Guilds WHERE id='{0}';'''.format(message.guild.id))
            guild = self.cursor.fetchone()

            if guild is not None:
                # Tell create the scheduler and tell the scheduler to send a message a certain time
                if repeat == 'daily':
                    self.scheduler.add_job(self.notifier, 'interval', start_date=(date.datetime - timedelta(hours=int(guild[2]))), days=1, id=eventid, kwargs={'gid': message.guild.id,'eventid': eventid})
                elif repeat == 'weekly':
                    self.scheduler.add_job(self.notifier, 'interval', start_date=(date.datetime - timedelta(hours=int(guild[3]))), weeks=1, id=eventid, kwargs={'gid': message.guild.id,'eventid': eventid})
                elif repeat == 'yearly':
                    self.scheduler.add_job(self.notifier, 'interval', start_date=(date.datetime - timedelta(hours=int(guild[4]))), days=365, id=eventid, kwargs={'gid': message.guild.id,'eventid': eventid})

            await message.channel.send('Event successfully updated')
        except Exception as inst:
            print(inst)
            await message.channel.send('There was an error editing your event, please retry.')

    ## Removes a recurring event from the list of recurring events
    async def remove(self, message, chunks):
        # Checks whether or not the command is valid
        if len(chunks) == 0:
            await message.channel.send('Usage: sudo remove <title>')
        
            return
        
        try:
            # Gets the title from the command
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)

            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))
            event = self.cursor.fetchone()
            role = message.guild.get_role(int(event[6]))
            await role.delete()

            # Removes the event from the sqlite3 database
            self.cursor.execute('''DELETE FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))
            self.cursor.execute('''DROP TABLE IF EXISTS `{0}`'''.format(eventid))

            if self.scheduler.get_job(eventid) is not None:
                self.scheduler.remove_job(eventid)

            await message.channel.send('Event successfully removed.')
        except Exception as inst:
            print(inst)
            await message.channel.send('There was an error removing your event, please retry.')

    ## Subscribes the user to a role which gets pinged with an event
    async def subscribe(self, message, chunks):
        # Checks whether or not the command is valid
        if len(chunks) == 0:
            await message.channel.send('Usage: sudo subscribe <title>')
        
            return
        
        try:
            # Gets the title from the command
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)

            self.cursor.execute(''' SELECT * FROM `{0}` WHERE member_id='{1}';'''.format(eventid, message.author.id))
            row = self.cursor.fetchone()
            # Check if server has already been added to guilds
            if row is None:
                self.cursor.execute('''INSERT INTO `{0}` VALUES ('{1}')'''.format(eventid, message.author.id))

            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))
            row = self.cursor.fetchone()

            if row is not None:
                await message.author.add_roles(message.guild.get_role(int(row[8])))

            await message.channel.send('You have subcribed to the event!')
        except Exception as inst:
            print(inst)
            await message.channel.send('You could not subscribe to the event.')

    ## Unsubscribes a user from receiving messages
    async def unsubscribe(self, message, chunks):
        # Checks whether or not the command is valid
        if len(chunks) == 0:
            await message.channel.send('Usage: sudo unsubscribe <title>')
        
            return
        
        try:
            # Gets the title from the command
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)

            self.cursor.execute(''' SELECT * FROM `{0}` WHERE member_id='{1}';'''.format(eventid, message.author.id))
            row = self.cursor.fetchone()
            # Check if server has already been added to guilds
            if row is not None:
                self.cursor.execute('''DELETE FROM `{0}` WHERE member_id='{1}')'''.format(eventid, message.author.id))

            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))
            row = self.cursor.fetchone()

            if row is not None:
                await message.author.remove_roles(message.guild.get_role(int(row[8])))

            await message.channel.send('You have unsubscribed from the event!')
        except Exception as inst:
            print(inst)
            await message.channel.send('You could not unsubscribe from the event.')

    ## Sends a notification about the event to all users that are subscribed to that event, this function is scheduled
    async def notifier(self, gid, eventid):
        try:
            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(gid, eventid))

            rows = self.cursor.fetchone()

            title = '***{0}***\n\n'.format(rows[1])
            description = '' if (rows[2] == 'N/A') else 'Description: {0}\n'.format(rows[2])
            time = dt(ttype="string", string=rows[3])
            time = time.datetime.strftime('Time: on %m-%d-%Y at %H:%M\n')
            location = '' if (rows[4] == 'N/A') else 'Location: {0}\n'.format(rows[4])
            link = '' if (rows[5] == 'N/A') else 'Link: {0}\n'.format(rows[5])

            await self.client.get_channel(int(rows[7])).send('{0}{1}{2}{3}{4}\n{5}'.format(title, description, time, location, link, self.client.get_guild(gid).get_role(int(rows[8])).mention))
        except Exception as inst:
            print(inst)
            return

    ## Gets and separates all then important information from a command
    async def parseOptions(self, chunks, message, description, date, location, link, repeat, channel):
        # Define what the event is and then add properties based on selected options
        mode = ''

        # Go through all the options and check what data needs to be parsed
        for chunk in chunks:
            if chunk == '-d':
                mode = '-d'

            elif chunk == '-t':
                mode = '-t'

            elif chunk == '-a':
                mode = '-a'

            elif chunk == '-l':
                mode = '-l'

            elif chunk == '-r':
                mode = '-r'

            elif chunk == '-c':
                mode = '-c'

            else:
                if mode == '-d':
                    description.append(chunk)

                elif mode == '-t':
                    date = dt(ttype='string', string=chunk)

                elif mode == '-a':
                    location.append(chunk)

                elif mode == '-l':
                    link = chunk

                elif mode == '-r':
                    repeat = chunk

                elif mode == '-c':
                    channel = message.channel_mentions[0].id

        if len(description) > 1:
            if description[0] == 'N/A':
                description = description[1:]

        if len(location) > 1:
            if location[0] == 'N/A':
                location = location[1:]

        # Reformat the data so that it is correct
        description = ' '.join(description)
        location = ' '.join(location)

        return description, date, location, link, repeat, channel

    async def parseTitle(self, chunks):
        title = []

        for chunk in chunks:
            if chunk != '-d' and chunk != '-r' and chunk != '-t' and chunk != '-c':
                title.append(chunk)
            else:
                break

        return ' '.join(title) 
        