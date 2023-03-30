import pandas as pd
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
from scipy import stats
import datetime
import datetime as dt
from os import system
from time import ctime


"""
連接 sql 引擎
"""
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)

db = pd.read_sql('monthly_revenue', engine).drop('index', axis=1)
db[['year', 'month']] = db.rev_period.str.split('/', expand=True)
# db.rev = round(db.rev/1000, 2)
print('完成DB撈資料', datetime.datetime.now())


"""
function
"""
def get_ratio(data):
    ttl_rev = data.rev.sum() / len(data) * 12
    data['ratio'] = round(data.rev/ttl_rev, 4)
    return data

def get_yoy(data):
    data.year = data.year.astype(int)
    data = data.sort_values('year')
    if data.rev.head(1).isnull== True:
        data['yoy％'] = 100
    else:
        data['yoy％'] = round(data.rev.diff()/data.rev.shift(1) * 100, 2)
    return data
    
def get_avg_ratio(data):
    if len(data) >= 5:
        weight = [1, 1, 1, 3, 5]
        roll_num = len(weight)
        data = data.sort_values('year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) == 4:
        weight = [1, 1, 2, 3]
        roll_num = len(weight)
        data = data.sort_values('year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) == 3:
        weight = [1, 1, 2]
        roll_num = len(weight)
        data = data.sort_values('year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) <= 2:
        return round(np.nanmean(data.ratio), 4)

ratio_df = pd.DataFrame(db['month'].unique()).rename({0:'month'}, axis=1)

def get_month_rev_predict_for_nxt_year(data):
#     print(data.st_code.head(1).values[0])
    if data.shape[0] >= 12:
        data = data.groupby('year').apply(get_ratio)
        ratio = data.groupby('month', as_index=False).apply(get_avg_ratio).set_axis(['month', 'wt_avg_ratio'],axis=1)
        data = pd.merge(data, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)
        predict_avg_annual_rev = round((data.rev/data.wt_avg_ratio).mean(), 4)
        data['rev'] = round(data.wt_avg_ratio * predict_avg_annual_rev, 2)
        data.year = data.year.astype(int) + 1
        data.rev_period = '* '+ data.year.astype(str) + '/' + data.month
        data = pd.concat([db[db.st_code == data.st_code.head(1).values[0]].tail(12), 
                          data], axis=0)
        data = data.groupby('month', as_index=False).apply(get_yoy)
        data['mom％'] = round(data.rev.pct_change(1) * 100, 2)
        return data.sort_values('rev_period').head(1)
    else:
        data = data.groupby('year').apply(get_ratio)
        ratio = data.groupby('month', as_index=False).apply(get_avg_ratio).set_axis(['month', 'wt_avg_ratio'],axis=1)
        ratio_len = ratio.month.shape[0]
        ratio = pd.merge(ratio_df, ratio, on='month', how='left').sort_values('month')
        ratio.wt_avg_ratio = ratio.wt_avg_ratio.fillna(round((1 - ratio.wt_avg_ratio.sum())/(12-ratio_len), 4))
        data = pd.merge(data, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)
        data[['st_code', 'st_name', 'year']] = data[['st_code', 'st_name', 'year']].fillna(method='pad')
        data.year = np.where(data.rev_period.isna() == False, data.year.astype(int) + 1, data.year)
        data.rev_period = '* ' + data.year.astype(str) + '/' + data.month
        predict_avg_annual_rev = round(np.nanmean(data.rev/data.wt_avg_ratio), 4)
        data['rev'] = round(data.wt_avg_ratio * predict_avg_annual_rev, 2)
        data = pd.concat([db[db.st_code == data.st_code.head(1).values[0]].tail(12), 
                          data], axis=0)
        data = data.groupby('month', as_index=False).apply(get_yoy)
        data['mom％'] = round(data.rev.pct_change(1) * 100, 2)
        return data.sort_values('rev_period').head(1)
    
print('完成讀function', datetime.datetime.now())


"""
整理營收worksheet
"""
update = pd.read_excel('/Users/yuchun/Revenue/tej_revenue_update.xlsm', 
                       sheet_name='工作表2', 
                       usecols=[3, 4, 5, 6, 7, 8], 
                       header=6)
update[['代號', '名稱']] = update['代號 名稱'].str.split(' ',expand=True).drop(2, axis=1)
update = update[update.iloc[:, 2].isna() == False]
update = update.rename({'【1】年月':'rev_period', 
                        '【4】單月營收成長率％':'yoy％', 
                        '【5】單月營收與上月比％':'mom％'}, axis=1)
update.iloc[:, 1] = pd.to_datetime(update.iloc[:, 1], format='%Y%m').dt.strftime('%Y/%m')
update.iloc[:, 2] = pd.to_datetime(update.iloc[:, 2], format='%Y%m%d').dt.strftime('%Y/%m/%d')
update.iloc[:, 3] = round(update.iloc[:, 3]/1000, 2)


"""
每月最新營收公布狀況
"""
latest = update.loc[:, ['代號', '名稱','【2】營收發布日', 
                        '【3】單月營收(千元)', 'yoy％','mom％']]
latest = latest.rename({'【2】營收發布日':'營收發布日', 
                        '【3】單月營收(千元)':'營收(百萬)'
                       }, axis=1).sort_values('yoy％', ascending=False)
latest_period = update.rev_period.head(1).values[0]
latest_filename = latest_period + '最新營收公布.csv'
latest.to_csv('/Users/yuchun/Revenue/Web2/models/{}'.format(latest_filename), 
              encoding='utf_8_sig', header=True, index=False)
# 完成最新營收更新csv
print('完成最新營收更新csv', datetime.datetime.now())


update = update.rename({'代號':'st_code', '名稱':'st_name',
                        '【2】營收發布日':'release_date', 
                        '【3】單月營收(千元)':'rev'}, axis=1)
update[['year', 'month', 'day']] = update['release_date'].astype(str).str.split('/', expand=True)

order = db.columns.values.tolist()
update = update[order]
update = update[~update.st_code.isin(db[db.rev_period == latest_period].st_code)]


"""
僅上傳新增的部分
"""
if update.shape[0] == 0:
    predict_nxt_month = db
else:
    update.to_sql('tej_revenue', engine, if_exists='append')
    predict_nxt_month = pd.concat([db, update], axis=0)
print('完成上傳新增的營收資訊', datetime.datetime.now())


"""
預估次月營收
"""
predict_order = db.columns.values.tolist()
predict_order.remove('release_date')
predict_order.remove('year')
predict_order.remove('month')

predict_nxt_month = predict_nxt_month.groupby('st_code', as_index=False).apply(get_month_rev_predict_for_nxt_year)
predict_nxt_month = predict_nxt_month[predict_order].reset_index(drop=True)
predict_nxt_month = predict_nxt_month.rename({'st_code':'代號', 'st_name':'名稱', 'rev':'營收(百萬)'}, axis=1)
predict_nxt_month_filename = predict_nxt_month.rev_period.head(1).values[0][2:] + '營收預估.csv'
predict_nxt_month.to_csv('/Users/yuchun/Revenue/Web2/models/{}'.format(predict_nxt_month_filename), 
                         encoding='utf_8_sig', 
                         header=True, 
                         index=False)
# 完成最新預估營收csv完整的
print('完成最新預估營收csv完整的', datetime.datetime.now())


"""
不同分類的預估營收名單： CB/個股期/濾產業的
"""
### 個股期 ###
futures_data = """
SELECT DISTINCT 標的證券 FROM 個股期歷史資料（近月及近二月）;
"""
st_future = pd.read_sql(futures_data, engine)
st_future['st_code'] = st_future['標的證券'].str[:4]
# predict_nxt_month_futures = predict_nxt_month[predict_nxt_month['代號'].isin(st_future.st_code)]
st_future.st_code.to_pickle("/Users/yuchun/Revenue/Web2/models/st_futures.pkl") 
print('完成個股期部分', datetime.datetime.now())


### 可轉債 ###
cb = pd.read_html('https://www.tpex.org.tw/web/bond/bonds_info/daily_trade/NewCb3itrade.php?l=zh-tw', encoding='utf_8')[0]
cb.columns = [''.join(col) for col in cb.columns.values]
cb = cb.rename({'代號代號':'代號', '名稱名稱':'名稱'}, axis=1)
# predict_nxt_month_cb = predict_nxt_month[predict_nxt_month['代號'].isin(cb['代號'].astype(str).str[:4]) == True]
cb['代號'].astype(str).str[:4].to_pickle('/Users/yuchun/Revenue/Web2/models/cb.pkl')
print('完成可轉債部分', datetime.datetime.now())


### 過濾產業 ###
industry = pd.read_sql('full_industry', engine).drop('index', axis=1)
filtered = industry[(industry['交易所產業分類'] != 'M1722 生技醫療') & 
                    (industry['交易所產業分類'] != 'M2326 光電業') &
                    (industry['交易所產業分類'] != 'M2331 其他電子業') &
                    (industry['交易所產業分類'] != 'M2500 建材營造') &
                    (industry['交易所產業分類'] != 'M2600 航運業') &
                    (industry['交易所產業分類'] != 'M2800 金融業') &
                    (industry['交易所產業分類'] != 'M2900 貿易百貨') &
                    (industry['交易所產業分類'] != 'M3200 文化創意業') &
                    (industry['TEJ產業分類'] != 'M25A 建設')
                   ]
# predict_nxt_month_filtered = predict_nxt_month[predict_nxt_month['代號'].isin(filtered.st_code.astype(str)) == True]
filtered.st_code.astype(str).to_pickle('/Users/yuchun/Revenue/Web2/models/filtered.pkl')
print('完成過濾產業', datetime.datetime.now())


"""
更新個股每日收盤資訊
"""
daily_trading_db = pd.read_sql('stock_daily_trading', engine).sort_values(['date', 'st_code'])
daily_trading_db = daily_trading_db.drop_duplicates()
daily_trading_db.date = pd.to_datetime(daily_trading_db.date).dt.strftime('%Y/%m/%d')

if (datetime.datetime.now().hour >= 15):
    try:
        today = datetime.datetime.today().strftime("%Y/%m/%d")
        otc_year = datetime.datetime.today().year - 1911
        otc_date = str(otc_year) + '/' + datetime.datetime.today().strftime("%Y/%m/%d")[5:]
        tse_date = ''.join(datetime.datetime.today().strftime("%Y/%m/%d").split('/'))

        tse_url = 'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date=' + tse_date + '&type=ALLBUT0999&response=html'
        otc_url = 'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&o=htm&d=' + otc_date + '&se=EW&s=0,asc,0'
        tse = pd.read_html(tse_url)[-1]
        otc = pd.read_html(otc_url)[0]
        tse.columns = tse.columns.droplevel(level=0)
        otc.columns = otc.columns.droplevel(level=0)
        otc = otc[otc['次日漲停價'].isna() == False]             # 把總共筆數刪掉

        otc['date'] = today
        tse['date'] = today

        otc = otc.loc[:, ['代號','名稱','date','開盤','最高','最低','收盤','成交股數']]
        otc = otc.set_axis(['st_code', 'st_name', 'date', 'open', 'high', 'low', 'close', 'volume'], axis=1)
        tse = tse.loc[:, ['證券代號','證券名稱','date','開盤價','最高價','最低價','收盤價','成交股數']]
        tse = tse.set_axis(['st_code', 'st_name', 'date', 'open', 'high', 'low', 'close', 'volume'], axis=1)
        tse = tse[(tse.open != '--') & (tse.close != '--') & (tse.open != '----')]
        otc = otc[(otc.open != '--') & (otc.close != '--') & (otc.open != '----')]

        daily_trading_update = pd.concat([tse, otc], axis=0)
        db_today = daily_trading_db[daily_trading_db.date == today]
        daily_trading_update = daily_trading_update[~daily_trading_update.st_code.isin(db_today[db_today.date == today].st_code)]

        if daily_trading_update.shape[0] > 0:
            daily_trading_update.to_sql('stock_daily_trading', engine, if_exists='append')
        else:
            pass
    except ValueError:
        pass
print('完成每日更新個股收盤資訊', datetime.datetime.now())


"""
機器學習分組相關
"""
cluster = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/cluster_industry.csv')
group = pd.merge(industry, cluster.loc[:, ['歆凱分組', '代號']].rename({'代號':'st_code'}, axis=1), on='st_code', how='left')
group['歆凱分組'] = np.where(group['歆凱分組'].isna() == True, 'ML無分組', group['歆凱分組'])
group.st_code = group.st_code.astype(str)

def latest_return(data):
    data['近一日漲跌％'] = round(data.close.pct_change(1)*100, 2)
    data['近一週漲跌％'] = round(data.close.pct_change(5)*100, 2)
    data['近一月漲跌％'] = round(data.close.pct_change(20)*100, 2)
    return data

ml_db = daily_trading_db[daily_trading_db.st_code.isin(group.st_code) == True].drop('index', axis=1)
ml_db = ml_db.groupby('st_code', as_index=False).apply(latest_return)


"""
最新的分組報酬
"""
ml_latest_return = ml_db.drop_duplicates('st_code', keep='last').loc[:, ['st_code', '近一日漲跌％', '近一週漲跌％', '近一月漲跌％']]
ml_latest_return = pd.merge(group, ml_latest_return, on='st_code', how='left')
ml_latest_return.to_csv('/Users/yuchun/Revenue/Web2/models/ml_latest_return.csv', 
                        encoding='utf_8_sig', header=True)
print('機器學習分組最新報酬完成', datetime.datetime.now())


"""
近一年的日報酬，繪圖用
"""
year_ago_date = ml_db.date.sort_values().drop_duplicates().tail(252).head(1).values[0]
latest_year_return = ml_db[ml_db.date >= year_ago_date].loc[:, ['st_code', '近一日漲跌％']]
latest_year_return.to_csv('/Users/yuchun/Revenue/Web2/models/latest_year_return.csv', 
                          encoding='utf_8_sig', header=True, index=False)
print('機器學習分組近一年報酬完成', datetime.datetime.now())


"""
上傳到 Github 上面
"""
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
upload.execute('Update_file')