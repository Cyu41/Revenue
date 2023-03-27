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
update['rev_period'] = pd.to_datetime(update['rev_period'], format='%Y%m').dt.strftime('%Y/%m')
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
predict_nxt_month = predict_nxt_month.sort_values('rev_period')
predict_nxt_month = predict_nxt_month.groupby('st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True)
predict_nxt_month = predict_nxt_month.groupby('st_code', as_index=False).apply(fn.get_predict).reset_index(drop=True)
predict_nxt_month = predict_nxt_month.drop_duplicates('st_code', keep='first')
predict_nxt_month = predict_nxt_month.drop(['declaration_date', 'declaration_year', 
                                            'declaration_month', 'Year', 'month'], axis=1)
predict_nxt_month = predict_nxt_month[predict_nxt_month.yoy <= 1000000000].sort_values('yoy', ascending=False)
predict_nxt_month.yoy = round(predict_nxt_month.yoy, 3)
predict_nxt_month.mom = round(predict_nxt_month.mom, 3)


# 輸出報表
filename = predict_nxt_month.rev_period.head(1).values[0][2:]
predict_nxt_month = predict_nxt_month.loc[:, ['st_code', 'st_name', 'rev_period', 'yoy', 'mom', 'rev', 'new_industry_name']]
predict_nxt_month = predict_nxt_month.rename({'st_code':'代號', 'st_name':'名稱', 'rev_period':'預估月', 
                                    'rev':'預估營收（百萬）', 'new_industry_name':'TEJ產業'}, axis=1)
predict_nxt_month.to_csv('/Users/yuchun/Revenue/Web2/models/{}營收預估.csv'.format(filename), 
                         encoding='utf_8_sig', 
                         header=True, 
                         index=False)


# 有發個股期的個股
futures_data = """
SELECT DISTINCT 標的證券 FROM 個股期歷史資料（近月及近二月）;
"""
st_future = pd.read_sql(futures_data, engine)
st_future['st_code'] = st_future['標的證券'].str[:4]
predict_nxt_month_f = predict_nxt_month[predict_nxt_month['代號'].isin(st_future.st_code)]
predict_nxt_month_f.to_csv('/Users/yuchun/Revenue/Web2/models/{}營收預估(個股期).csv'.format(filename), 
                           encoding='utf_8_sig', header=True, index=False)


# 最新公告營收報表
update = pd.read_excel("/Users/yuchun/Revenue/2022月營收更新報表_yuchun.xlsm", sheet_name='工作表1', header=6,
                       usecols=[3,4], names=['name', 'rev_period'])

latest = update.sort_values('rev_period').rev_period.tail(1).values[0]
latest_data = db.groupby('st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True)
latest_data = latest_data.loc[:, ['st_code', 'st_name', 'rev_period', 'rev', 'mom', 'yoy', 'new_industry_name']]
latest_data = latest_data[latest_data.rev_period == latest]
latest_data.yoy = round(latest_data.yoy, 3)
latest_data.mom = round(latest_data.mom, 3)
latest_data = latest_data.rename({'st_code':'代號', 'st_name':'名稱', 'rev_period':'月份', 'rev':'預估營收（百萬）'}, axis=1)
latest_data.to_csv('/Users/yuchun/Revenue/Web2/models/{}最新營收公布.csv'.format(latest), 
                         encoding='utf_8_sig', 
                         header=True, 
                         index=False)