import sqlite3
import sched, time
from modules.dt import dt
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from datetime import timedelta

class master_scheduler:
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
            '-r <yearly, weekly, daily> specify how often you want the event to repeat\n' \
            '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n')

            return
        
        # Don't crash the bot if something goes wrong
        try:
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)

            # Get information from the array of inputs
            description, date, repeat, channel = await self.parseOptions(chunks, message, [], dt(ttype="time"), 'weekly', message.channel.id)

            # Add the data to a SQL table
            
            self.cursor.execute(''' SELECT * FROM Guilds WHERE id='{0}';'''.format(message.guild.id))
            row = self.cursor.fetchone()
            # Check if server has already been added to guilds
            if row is None:
                self.cursor.execute('''INSERT INTO Guilds VALUES ('{0}', 'G_{0}', '6', '24', '72')'''.format(message.guild.id))
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS G_{0}(id TEXT NOT NULL PRIMARY KEY, title TEXT, description TEXT, date TEXT, repeat TEXT, channel INT);'''.format(message.guild.id))
            self.cursor.execute('''INSERT INTO G_{0} VALUES ('{1}', '{2}', '{3}', '{4}', '{5}', '{6}');'''.format(message.guild.id, eventid, title, description, str(date), repeat, channel))
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

            print(self.scheduler.get_jobs()[0].trigger.start_date)

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
            '-r <yearly, weekly, daily> specify how often you want the event to repeat\n' \
            '-t <date/time> indicate what day and time to start at using the following format MM-DD-YYYYThh:mm\n')

            return

        try:
            title = await self.parseTitle(chunks)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)
            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))

            row = self.cursor.fetchone()

            description, date, repeat, channel = await self.parseOptions(chunks, message, row[2], dt(ttype="string", string=row[3]), row[4], row[5])

            # Update the sqlite3 database
            self.cursor.execute('''UPDATE G_{0} SET description='{1}', date='{2}', repeat='{3}', channel='{4}' WHERE id='{5}';'''.format(message.guild.id, description, str(date), repeat, channel, eventid))

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

            # Removes the event from the sqlite3 database
            self.cursor.execute('''DELETE FROM G_{0} WHERE id='{1}';'''.format(message.guild.id, eventid))
            self.cursor.execute('''DROP TABLE IF EXISTS {0}'''.format(eventid))

            if self.scheduler.get_job(eventid) is not None:
                self.scheduler.remove_job(eventid)

            await message.channel.send('Event successfully removed.')
        except:
            await message.channel.send('There was an error removing your event, please retry.')

    ## Sends a notification about the event to all users that are subscribed to that event, this function is scheduled
    async def notifier(self, gid, eventid):
        try:
            self.cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(gid, eventid))

            rows = self.cursor.fetchone()

            await self.client.get_channel(int(rows[5])).send('{0}\n\n{1}'.format(rows[1], rows[2]))
        except Exception as inst:
            print(inst)
            return

    ## Gets and separates all then important information from a command
    async def parseOptions(self, chunks, message, description, date, repeat, channel):
        # Define what the event is and then add properties based on selected options
        mode = ''

        # Go through all the options and check what data needs to be parsed
        for chunk in chunks:
            if chunk == '-d':
                mode = '-d'

            elif chunk == '-r':
                mode = '-r'

            elif chunk == '-t':
                mode = '-t'

            elif chunk == '-c':
                mode = '-c'

            else:
                if mode == '-d':
                    description.append(chunk)

                elif mode == '-r':
                    repeat = int(chunk)

                elif mode == '-t':
                    date = dt(ttype='string', string=chunk)

                elif mode == '-c':
                    channel = message.channel_mentions[0].id


        # Reformat the data so that it is correct
        description = ' '.join(description)

        return description, date, repeat, channel

    async def parseTitle(self, chunks):
        title = []

        for chunk in chunks:
            if chunk != '-d' and chunk != '-r' and chunk != '-t' and chunk != '-c':
                title.append(chunk)
            else:
                break

        return ' '.join(title) 
        