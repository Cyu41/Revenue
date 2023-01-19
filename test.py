import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
import numpy as np
from Upload_git import upload
from os import system
import time
from time import ctime, sleep
from Upload_git import upload
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine

"""
connect to db
"""
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)

stock_info = pd.read_csv('stock_info.csv')
stock_info.st_code = stock_info.st_code.astype(str)


"""
search in sql
"""
mask = ""
ind_search = """
select rev_period, sum(rev) as ttl_rev 
from tej_revenue 
where {} 
group by rev_period;
""".format(mask)

st_search = """
select st_code, st_name, rev_period, declaration_date, rev
from tej_revenue 
where {};
""".format(mask)


"""
callback input & output detail 
"""
revenue = pd.read_sql('industry', engine)
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()
dropdown1 = new_industry_name[2]
dropdown2 = minor_industry_name[1]
st_input = '2330'
year = [2018, 2023]


def get_st_mom_yoy(data):
    data['mom'] = data.rev.diff()/data.rev.shift(1)
    data['Year'] =  data.rev_period.astype(str).str[0:4]
    data['month'] = data.rev_period.astype(str).str[5:7]
    def get_yoy(data):
        data = data.sort_values('Year')
        data['yoy'] = data.rev.diff()/data.rev.shift(1)
    yoy = pd.DataFrame()
    yoy = data.groupby('month').apply(get_yoy)
    return yoy

dropdown1 = new_industry_name[1]
dropdown2 = '' #minor_industry_name[5] #None
st_input = ''

if st_input is None or st_input == '':
    if dropdown1 is not None and dropdown2 is None or dropdown2 == '':
        mask = ("new_industry_name = '" + dropdown1 + "'")
    elif dropdown1 is None and dropdown2 is not None or dropdown1 == '':
        mask = ("minor_industry_name = '" + dropdown2 + "'")
    elif dropdown1 is not None and dropdown2 is not None:
        mask = ("new_industry_name = '" + dropdown1 + "' and " + "minor_industry_name = '" + dropdown2 + "'")
    data = pd.read_sql(st_search, engine)
    data = data.groupby(by='st_code', as_index=False).apply(get_st_mom_yoy)
    latest = data.drop_duplicates(subset='st_code', keep='last').drop('index', axis=1)
    latest = latest.loc[:, ['st_code', 'st_name', 'declaration_date', 'rev', 'mom', 'yoy']]
    latest.columns.values
    # 轉換成產業總營收
    data = data.groupby(by='rev_period', as_index=False).agg({'rev':'sum'})

else:
    if (st_input.isdigit() == True):
        industry = stock_info[stock_info.st_code == st_input].new_industry_name.values[0]
        mask = ("new_industry_name = '" + industry + "'")
    else:
        industry = stock_info[stock_info.st_name == st_input].new_industry_name.values[0]
        mask = ("new_industry_name = '" + industry + "'")
    print(mask)
    data = pd.read_sql(st_search, engine)     # 產業資料
    # 轉換成個股總營收
    latest = data.drop_duplicates(subset='st_code', keep='last')
    
    
        

#new_industry_name = 'M1100 水泥工業'
sql = """select * from tej_revenue where {};""".format(mask)
pd.read_sql(sql, engine)
dropdown1
# ['index', 'st_code', 'st_name', 'rev_period', 'declaration_date',
#  'rev', 'declaration_year', 'declaration_month', 'new_industry_name', 
#  'minor_industry_name'] 

# 有字：數字 or 文字
# 沒字：new_industry_name or minor_industry_name or 兩個都有
# 
years = [str(year[0]),str(year[1])]




upload.execute('Update_file')
# pd.read_csv('db.csv', low_memory=False)