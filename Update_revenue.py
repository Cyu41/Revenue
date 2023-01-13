import pandas as pd
from os import system
from time import ctime, sleep
from Upload_git import upload

db = pd.read_csv("data_visualize.csv", low_memory=False)
update = pd.read_excel("2022月營收更新報表_yuchun.xlsx", sheet_name='工作表2', header=6)
# update
########################
#      整理資料        #
########################
update = update.iloc[:, 3:7]
update = update.rename({'【1】年月':'date', '【2】營收發布日':'annouce_day', 
                        '【3】單月營收(千元)':'rev'}, axis=1)
update['st_code'] = update['代號 名稱'].astype(str).str[0:4]
update['st_name'] = update['代號 名稱'].astype(str).str[5:7]

update['annouce_day'] = update['annouce_day'].astype(str)
update['Year'] = update['annouce_day'].str[0:4]
update['month'] = update['annouce_day'].str[4:6]
update['annouce_day'] = update['annouce_day'].str[0:4] + "/" + update['annouce_day'].str[4:6] + "/" + update['annouce_day'].str[6:8]
update = update[update.annouce_day != 'nan//'].drop('代號 名稱', axis=1)

db = pd.concat([db, update], axis=0).to_csv('db.csv', encoding='utf_8_sig', header=None)

sleep(3)

# upload = Auto_push_to_github()
upload.execute('Update_file')
# class Auto_push_to_github(object):
#     def get_time(self):
#         return ctime()
#     def create_git_order(self, time, msg):
#         order_arr = ["git add *", "git commit -m" + '"' + 
#                      time +':' + msg + '"' + "git push origin master"]
#         for order in order_arr:
#             system(order)
#     def execute(self, msg):
#         dates = self.get_time()
#         self.create_git_order(dates, msg)


