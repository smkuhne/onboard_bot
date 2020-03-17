import sqlite3
import sched, time
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

class master_scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    async def events(self, message, csplit, c):
        await message.channel.send('The following events where created on this server:')

        c.execute('''SELECT * FROM G_{0}'''.format(message.guild.id))
        rows = c.fetchall()

        for row in rows:
            await message.channel.send('"{0}"'.format(row[1]))

    ## Allows for the creation of a new recurring event
    async def create(self, message, csplit, c):

        # If the command is used incorrectly, tell the user what they are doing wrong
        if len(csplit) < 3:
            await message.channel.send('Usage: sudo create <title> [options]\n\n' \
            'Where options include:\n\n' \
            '-b <before> to indicate how many hours before a user should be notified\n' \
            '-d <description> to set a description\n' \
            '-r <days> number of days it takes to repeat\n' \
            '-s <date> indicating the day on which to start with format MM-DD-YYYY\n' \
            '-t <time> indicating what hour the event is taking place (1-24)')

            return
        
        # Don't crash the bot if something goes wrong
        try:

            # Define what the event is and then add properties based on selected options
            title = [csplit[2]]
            description = []
            date = datetime.now()
            date = date.replace(minute=0, second=0, microsecond=0)
            before = 24
            repeat = 7
            mode = '-c'

            for option in csplit[3:]:
                if option == '-b':
                    mode = '-b'

                elif option == '-d':
                    mode = '-d'

                elif option == '-r':
                    mode = '-r'

                elif option == '-s':
                    mode = '-s'

                elif option == '-t':
                    mode = '-t'

                else:
                    if mode == '-b':
                        before = int(option)

                    elif mode == '-d':
                        description.append(option)

                    elif mode == '-r':
                        repeat = int(option)
                    
                    elif mode == '-s':
                        date = datetime.strptime(option, '%m-%d-%Y')

                        date = date.replace(year=date.year, month=date.month, day=date.day)

                    elif mode == '-t':
                        date = date.replace(hour=int(option))

                    elif mode == '-c':
                        title.append(option)

            # Reformat the data so that it is correct
            description = ' '.join(description)
            title = ' '.join(title)
            eventid = 'G_{0}_{1}'.format(message.guild.id, title)

            # Add the data to a SQL table
            c.execute('''CREATE TABLE IF NOT EXISTS G_{0}(id TEXT NOT NULL PRIMARY KEY, title TEXT, description TEXT, date TEXT, before INT, repeat INT);'''.format(message.guild.id))
            c.execute('''INSERT INTO G_{0} VALUES ('{1}', '{2}', '{3}', '{4}', '{5}', '{6}');'''.format(message.guild.id, eventid, title, description, date.strftime('%Y-%m-%dT%H:%M'), before, repeat))
            c.execute('''CREATE TABLE IF NOT EXISTS `{0}`(member_id INT);'''.format(eventid))

            # Confirm successfull creation of the event
            await message.channel.send('Your event {0}, has been created'.format(title))

            # Tell create the scheduler and tell the scheduler to send a message a certain time
            self.scheduler.add_job(self.notifier, 'interval', start_date=date, days=repeat, id=eventid, kwargs={'channel': message.channel, 'cursor': c, 'gid': message.guild.id,'eventid': eventid})
        except Exception as inst:
            print(inst)
            await message.channel.send('There was an error creating your event, please retry.')
    
    async def edit(self, message, csplit, c):
        await message.channel.send('Edit event')

    async def remove(self, message, csplit, c):
        await message.channel.send('Remove event')

    async def notifier(self, channel, cursor, gid, eventid):
        try:
            cursor.execute('''SELECT * FROM G_{0} WHERE id='{1}';'''.format(gid, eventid))

            rows = cursor.fetchall()

            await channel.send('{0}\n\n{1}'.format(rows[0][1], rows[0][2]))
        except:
            return

    async def setup(self, c):
        print('Currently setting up all events again.')