import re
import os
import json
from datetime import datetime
from pathlib import Path

class event:
    def __init__(self, client):
        self.client = client
        self.stage = 0
        self.error_stage = 0

    # Creates an event including various stages of completion
    async def create(self, message):
        success = 0

        if self.stage == 0:

            # Gets title, asks for description
            self.title = re.sub('\$event\s*', '', message.content)
            await self.send(message)
            self.stage += 1
            success = 1

        elif self.stage == 1:

            # Gets description, asks for date
            self.description = re.sub('\$event\s*', '', message.content)
            await self.send(message)
            self.stage += 1
            success = 1

        elif self.stage == 2:

            # Gets date and time, asks for location
            self.date = re.sub('\$event\s*', '', message.content)

            try:
                self.date = datetime.strptime(self.date, '%b %d %Y %I:%M%p')
            except ValueError as e:
                self.success = False
                return self.success
            await self.send(message)
            self.stage += 1
            success = 1

        elif self.stage == 3:

            # Gets location, makes sure user wants to create event
            self.location = re.sub('\$event\s*', '', message.content)
            self.message = '**{}**\n\n{}\n\nDate: {}\n\nLocation: {}'.format(self.title, self.description, self.date, self.location)
            await self.send(message)
            self.stage += 1
            success = 1

        elif self.stage == 4:

            # Checks if user wants to save event
            if re.sub('\$event\s*', '', message.content).lower() == 'y':
                await self.save(message)
                await message.channel.send('Successfully created event!')
                success = 2

        elif self.stage == 99:
            if re.sub('\$event\s*', '', message.content).lower() == 'y':
                self.stage = self.error_stage
                await self.send(message)
                self.stage += 1
                success = 1

        # Return validity of input
        return success

    async def send(self, message):
        if self.stage == 0:
            await message.channel.send('Enter a description for the event:')

        elif self.stage == 1:
            await message.channel.send('Enter a date and time for the event, (Example Jan 1 2020 11:43AM):')

        elif self.stage == 2:
            await message.channel.send('Enter a location for the event:')

        elif self.stage == 3:
            await message.channel.send('{}\n\nIs this correct? (y/n)'.format(self.message))

    async def error(self, message):
        await message.channel.send('There was an error processing your entry, continue? (y/n)')
        self.error_stage = self.stage - 1

        self.stage = 99

    async def save(self, message):
        d = Path().resolve()

        if not os.path.exists('{}/events/{}'.format(d, message.guild.name)):
            os.makedirs('{}/events/{}'.format(d, message.guild.name))

        json_file = open('{}/events/{}/test.json'.format(d, message.guild.name), 'w')

        json_event = {
            'title': self.title,
            'description': self.description,
            'date': self.date.strftime('%m/%d/%Y, %H:%M:%S'),
            'location': self.location
        }

        json.dump(json_event, json_file)

