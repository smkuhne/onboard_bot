# Onboard Bot

The onboard bot script allows users to create events that will send notification in a recurring nature. Server users can subscribe to events which will give them the corresponding role, which will be pinged before the event occurs.

## Hosting Setup

Clone the project and then open a terminal in the project directory.

The following command will set up the database:
``` shell
mkdir database && cd database && events.db && cd ../
```

Then make a file called variables.py in the main project directory with that is formatted as follows, enter your own bot token and timezone:
``` python
token = "bot_token"
zone = "timezone"
```

## Bot Usage

All commands have the following format

``` shell
sudo <command> <input> [options]
```

In order to get information on the commands, use:

``` shell
sudo help
```

## Usage Terms and Conditions

The software is provided as is and I accept no liability for any consequences of hosting the bot. Do not redistribute this bot for any sort of commercial gain. You are free to modify the software, but must provide some sort of reference to the original project when posting on your github, or other public repository.