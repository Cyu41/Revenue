import pandas as pd
import datetime
from sqlalchemy import create_engine

# 連接 sql 引擎
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)

otc_year = datetime.datetime.today().year - 1911
otc_date = str(otc_year) + '/' + datetime.datetime.today().strftime("%Y/%m/%d")[5:]
tse_date = ''.join(datetime.datetime.today().strftime("%Y/%m/%d").split('/'))

tse_url = 'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date=' + tse_date + '&type=ALLBUT0999&response=html'
otc_url = 'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&o=htm&d=' + otc_date + '&se=EW&s=0,asc,0'
tse = pd.read_html(tse_url)[-1]
otc = pd.read_html(otc_url)[0]
tse.columns = tse.columns.droplevel(level=0)
otc.columns = otc.columns.droplevel(level=0)
otc = otc[otc['次日漲停價'].isna() == False]

otc['date'] = datetime.datetime.today().strftime("%Y/%m/%d")
tse['date'] = datetime.datetime.today().strftime("%Y/%m/%d")

otc = otc.loc[:, ['代號','名稱','date','開盤','最高','最低','收盤','成交股數']]
otc = otc.set_axis(['st_code', 'st_name', 'date', 'open', 'high', 'low', 'close', 'volume'], axis=1)
tse = tse.loc[:, ['證券代號','證券名稱','date','開盤價','最高價','最低價','收盤價','成交股數']]
tse = tse.set_axis(['st_code', 'st_name', 'date', 'open', 'high', 'low', 'close', 'volume'], axis=1)
tse = tse[(tse.open != '--') & (tse.close != '--') & (tse.open != '----')]
otc = otc[(otc.open != '--') & (otc.close != '--') & (otc.open != '----')]

# Update to sql
tse.to_sql('daily_trading', engine, if_exists='append')
otc.to_sql('daily_trading', engine, if_exists='append')