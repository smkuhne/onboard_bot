from datetime import datetime
from variables import zone
from pytz import timezone

class standardtime:
    def __init__(self, ttype, time=datetime.now(timezone(zone)), string=""):
        if ttype == 'time':
            self.datetime = time
        elif ttype == 'string':
            self.datetime = datetime.strptime(string, '%m-%d-%YT%H:%M%z')

    def __str__(self):
        return self.datetime.strftime('%m-%d-%YT%H:%M%z')
    