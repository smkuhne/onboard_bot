from datetime import datetime

class dt:
    def __init__(self, ttype, time=datetime.now(), string=""):
        if ttype == 'time':
            self.datetime = time
        elif ttype == 'string':
            self.datetime = datetime.strptime(string, '%m-%d-%YT%H:%M')

    def __str__(self):
        return self.datetime.strftime('%m-%d-%YT%H:%M')
    