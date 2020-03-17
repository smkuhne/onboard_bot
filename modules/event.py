import re
import os
import json
import sqlite3
import sched, time
from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from pathlib import Path

async def events(message, csplit, c):
    await message.channel.send('These are the available events')

## Allows for the creation of a new recurring event
async def create(message, csplit, c):

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
        event = {}
        event['title'] = [csplit[2]]
        event['description'] = []
        event['date'] = datetime.now()
        event['date'] = event['date'].replace(minute=0, second=0, microsecond=0)
        event['before'] = 24
        event['repeat'] = 7
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
                    event['before'] = int(option)

                elif mode == '-d':
                    event['description'].append(option)

                elif mode == '-r':
                    event['repeat'] = int(option)
                
                elif mode == '-s':
                    date = datetime.strptime(option, '%m-%d-%Y')

                    event['date'] = event['date'].replace(year=date.year, month=date.month, day=date.day)

                elif mode == '-t':
                    event['date'] = event['date'].replace(hour=int(option))

                elif mode == '-c':
                    event['title'].append(option)

        # Reformat the data so that it is correct
        event['date'] = event['date'].strftime('%Y-%m-%dT%H:%M')
        event['description'] = ' '.join(event['description'])
        event['title'] = ' '.join(event['title'])
        event['message'] = '{0}\n\n{1}'.format(event['title'], event['description'])

        # Add the data to a SQL table
        c.execute('''CREATE TABLE IF NOT EXISTS G_{0}(title TEXT, description TEXT, date TEXT, before INT, repeat INT);'''.format(message.guild.id))
        c.execute('''INSERT INTO G_{0} VALUES ('{1}', '{2}', '{3}', '{4}', '{5}');'''.format(message.guild.id, event['title'], event['description'], event['date'], event['before'], event['repeat']))
        c.execute('''CREATE TABLE IF NOT EXISTS `G_{0}_{1}`(member_id INT);'''.format(message.guild.id, event['title']))

        # Confirm successfull creation of the event
        await message.channel.send('Your event {0}, has been created'.format(event['title']))

        # Tell create the scheduler and tell the scheduler to send a message a certain time
        scheduler = AsyncIOScheduler()
        scheduler.start()
        scheduler.add_job(notifier, 'date', run_date=datetime.strptime(event['date'],'%Y-%m-%dT%H:%M'), id='G_{0}_{1}'.format(message.guild.id, event['title']), kwargs={'message': message, 'text': event['message']})
    except Exception as inst:
        print(inst)
        await message.channel.send('There was an error creating your event, please retry.')

async def edit(message, csplit, c):
    await message.channel.send('Edit event')

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

async def notifier(message, text):
    try:
        await message.channel.send(text)
        print("Ran a thing!")
    except:
        return

