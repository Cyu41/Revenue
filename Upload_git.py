from os import system
from time import ctime

class Auto_push_to_github(object):
    def get_time(self):
        return ctime()

    def create_git_order(self, time, msg):
        order_arr = ["git add *","git commit -m " + '"' + time + ': ' + msg + '"',"git push origin main"]
        for order in order_arr:
            system(order)
    
    def execute(self, msg):
        dates = self.get_time()
        self.create_git_order(dates, msg)

upload = Auto_push_to_github()
# upload.execute('Upload_git')