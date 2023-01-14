import pandas as pd
from os import system
import time
from time import ctime, sleep
from Upload_git import upload
import schedule

import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine


update = pd.read_excel("2022月營收更新報表_yuchun.xlsx", sheet_name='工作表2', header=6)
update = update.iloc[:, 3:7]
update = update.rename({'【1】年月':'rev_period', '【2】營收發布日':'declaration_date', '【3】單月營收(千元)':'rev'}, axis=1)
update['st_code'] = update['代號 名稱'].astype(str).str[0:4]
update['st_name'] = update['代號 名稱'].astype(str).str[5:]
update['declaration_date'] = update['declaration_date'].astype(str)
update['declaration_year'] = update['declaration_date'].str[0:4]
update['declaration_month'] = update['declaration_date'].str[4:6]
update['rev_period'] = update['rev_period'].astype(str).str[0:4] + "/" + update['rev_period'].astype(str).str[4:6]
update['declaration_date'] = update['declaration_date'].str[0:4] + "/" + update['declaration_date'].str[4:6] + "/" + update['declaration_date'].str[6:8]
update = update[update.declaration_date != 'nan//'].drop('代號 名稱', axis=1)

db = pd.read_csv('db.csv', low_memory=False).reset_index(inplace=False, drop=True)
db['st_code'] = db['st_code'].astype(str)
order = db.columns.values.tolist()
stock_info = db.loc[:, ['st_code', 'st_name', 'new_industry_name', 'minor_industry_name']].drop_duplicates(keep='first')
update = pd.merge(update, stock_info, on=['st_name','st_code'], how='outer')
update = update[order]


# 測試連線 PostgreSQL
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine(
    'postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, database), echo=True)
# db.to_sql('tej_revenue', engine)
update.to_sql('tej_revenue', engine, if_exists='append')

engine.dispose()

upload.execute('Update_file')