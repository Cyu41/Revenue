import pandas as pd
from os import system
import time
from time import ctime, sleep
from Upload_git import upload
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.dialects.postgresql import insert


def insert_on_duplicate(table, conn, keys, data_iter):
    print(list(data_iter))
    insert_stmt = insert(table.table).values(list(data_iter))
    on_duplicate_key_stmt = insert_stmt.on_conflict_do_nothing(
        constraint='tej_revenue_pk'
    )
    print(on_duplicate_key_stmt)
    conn.execute(on_duplicate_key_stmt)


# def auto_update_tej_revenue():
update = pd.read_excel("2022月營收更新報表_yuchun.xlsm", sheet_name='工作表1', header=6)
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

latest = update.sort_values('declaration_date').declaration_date.drop_duplicates().tail(1).values[0]
update = update[update.declaration_date == latest]

# write a df to a PostgreSQL database
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"


engine = create_engine(
    'postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)


db = pd.read_csv('db.csv', low_memory=False).reset_index(inplace=False, drop=True)
db['st_code'] = db['st_code'].astype(str)
order = db.columns.values.tolist()
stock_info = db.loc[:, ['st_code', 'st_name', 'new_industry_name', 'minor_industry_name']].drop_duplicates(keep='first')
update = pd.merge(update, stock_info, on=['st_name','st_code'], how='inner')
update = update[order]
# update.to_sql('tej_revenue', con=engine, if_exists='append')

for i in range(len(update)):
    try:
        update.iloc[i:i+1].to_sql('tej_revenue', con=engine, if_exists='append')
    except sqlalchemy.exc.IntegrityError: 
        pass #or any other action

# update.to_sql('tej_revenue', con=engine.connect(), if_exists='append', method=insert_on_duplicate)

print(ctime(), 'updated to the latest revenue')
# engine.dispose()

# schedule.every(5).seconds.do(auto_update_tej_revenue)
# time.sleep(3)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
# sys.exit()

upload.execute('Update_file')