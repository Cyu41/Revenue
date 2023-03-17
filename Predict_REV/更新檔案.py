import pandas as pd
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
from scipy import stats
import function as fn


# 連接 sql 引擎
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)


# 讀取資料庫中的資料
db = pd.read_sql('tej_revenue', engine).drop('index', axis=1)
db['rev'] = round(db['rev']/1000, 2)


# 讀取更新報表
update = pd.read_excel("/Users/yuchun/Revenue/2022月營收更新報表_yuchun.xlsm", sheet_name='工作表1', header=6,
                       usecols=[3,4,5,6], names=['name', 'rev_period', 'declaration_date', 'rev'])
update[['st_code', 'st_name']] = update['name'].astype(str).str.split(n=1, expand=True)
update['declaration_date'] = pd.to_datetime(update['declaration_date'], format='%Y%m%d').dt.strftime('%Y/%m/%d')
update[['declaration_year', 'declaration_month', 'day']] = update['declaration_date'].astype(str).str.split('/', expand=True)
update = update.drop('day', axis=1)
update['rev_period'] = update['rev_period'].astype(str).str[:4] + "/" + update['rev_period'].astype(str).str[4:6]
update = update[update.declaration_date != 'nan//'].drop('name', axis=1)


# 合併欄位及資料庫資訊
order = db.columns.values.tolist()
stock_info = db.loc[:, ['st_code', 'new_industry_name', 'minor_industry_name']].drop_duplicates(keep='first')
update = pd.merge(update, stock_info, on=['st_code'], how='inner')
update = update[order]
latest = update.rev_period.head(1).values[0]
update = update[~update.st_code.isin(db[db.rev_period == latest].st_code)]


#上傳新增的部分
if update.shape[0] == 0:
    predict_nxt_month = db
else:
    update.to_sql('tej_revenue', engine, if_exists='append')
    predict_nxt_month = pd.concat([db, update], axis=0)


# 預估次月營收
predict_nxt_month = predict_nxt_month.groupby('st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True)
predict_nxt_month = predict_nxt_month.groupby('st_code', as_index=False).apply(fn.get_predict).reset_index(drop=True)
predict_nxt_month = predict_nxt_month.drop_duplicates('st_code', keep='first')
predict_nxt_month = predict_nxt_month.drop(['declaration_date', 'declaration_year', 
                                            'declaration_month', 'Year', 'month'], axis=1)


# 輸出報表
filename = predict_nxt_month.rev_period.head(1).values[0][2:]
predict_nxt_month.to_csv('/Users/yuchun/Revenue/Predict_REV/{}營收預估.csv'.format(filename), 
                         encoding='utf_8_sig', 
                         header=True, 
                         index=False)