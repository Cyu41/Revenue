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
from sklearn.linear_model import LinearRegression
from statsmodels.regression.rolling import RollingOLS, RollingWLS
from scipy import stats
import revenue_function as fn
import pickle



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

"""
callback input & output detail 
"""
revenue = pd.read_sql('industry', engine)
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()
db = pd.read_sql('tej_revenue', engine).drop('index', axis=1)
db['rev'] = round(db['rev']/1000, 2)
db = db.groupby('st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True)
stock_info = revenue.iloc[:, 1:4].rename({'TSE新產業名':'new_industry_name',
                                          'TEJ子產業名':'minor_industry_name'}, axis=1)
stock_info['st_code'] = stock_info['公司簡稱'].str[0:4]
stock_info['st_name'] = stock_info['公司簡稱'].str[5:]
stock_info = stock_info.drop('公司簡稱', axis=1)

"""
function for predict data
"""
def get_ratio(data):
    ttl_rev = data.rev.sum()/len(data)*12
    data['ratio'] = round(data.rev/ttl_rev, 4)
    return data


def get_avg_ratio(data):
    if len(data) >= 5:
        weight = [1, 1, 1, 3, 5]
        roll_num = len(weight)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) >= 4:
        weight = [1, 1, 2, 3]
        roll_num = len(weight)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) >= 3:
        weight = [1, 1, 2]
        roll_num = len(weight)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) >= 2:
        roll_num = len(data)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(data.ratio.mean(), 4)

def get_predict(data):
    # new_industry_list = ['M1722 生技醫療', 'M2500 建材營造', 'M9900 其他', 'M1200 食品工業']
    # minor_industry_list = ['M25A 建設']
    # if (data.new_industry_name.head(1).isin(new_industry_list).values[0] == False) & (data.new_industry_name.head(1).isin(minor_industry_list).values[0] == False):
    if data.shape[0] >= 10:
        a = data.groupby('Year', as_index=False).apply(get_ratio)
        ratio = pd.DataFrame(a.groupby('month', as_index=False).apply(get_avg_ratio)).set_axis(['month', 'wt_avg_ratio'],axis=1)
        predict = pd.merge(a, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(13)  # 僅向後預測一年
        predict['predict_annul_rev'] = round(predict.rev / predict.ratio)
        predict['predict_month_rev'] = round(predict['predict_annul_rev'].tail(12).mean()* predict.wt_avg_ratio)
        predict['Year'] = (predict.Year.astype(int) + 1).astype(str)
        predict['rev'] = predict['predict_month_rev']
        predict = pd.concat([data.sort_values('rev_period'), predict], axis=0).sort_values(['Year', 'month'])
        predict['mom'] = predict.rev.diff() / predict.rev.shift(1)
        predict = predict.groupby('month', as_index=False).apply(fn.get_yoy).sort_values(['Year', 'month'])
        predict['rev_period'] = '* ' + predict.Year + '/' + predict.month
        predict = predict.drop(['ratio','wt_avg_ratio','predict_annul_rev','predict_month_rev'], axis=1)
        return predict.tail(12)
    else:
        print(data.st_code.head(1).values[0], data.shape[0])
    # else:
    #     print(data.st_code.head(1).values[0], data.new_industry_name.head(1).values[0], '產業不可測')


dropdown1 = new_industry_name[1]
dropdown2 = minor_industry_name[0]
st_input = '2412'
st_or_group = '產業'

data = db
if (st_input == ''):
    if (dropdown1 != new_industry_name[0]) & (dropdown2 == minor_industry_name[0]):
        rev_data = data[(data.new_industry_name == dropdown1)]
        title = dropdown1 + ' '
        
    elif (dropdown1 != new_industry_name[0]) & (dropdown2 != minor_industry_name[0]):
        rev_data = data[(data.new_industry_name == dropdown1) & 
                        (data.minor_industry_name == dropdown2)]
        title = dropdown1 + dropdown2 + ' '
        
    elif (dropdown1 == new_industry_name[0]) & (dropdown2 != minor_industry_name[0]):
        rev_data = data[(data.minor_industry_name == dropdown2)]
        title = dropdown2 + ' '


else:
    if st_or_group == '個股':
        rev_data = data[data.st_code == st_input]
        title = st_input + ' ' + rev_data.st_name.head(1).values[0] + ' '

    elif st_or_group == '產業':
        new_index = data[data.st_code == st_input].new_industry_name.head(1).values[0]
        minor_index = data[data.st_code == st_input].minor_industry_name.head(1).values[0]
        if (new_index != '') & (minor_index != ''):
            rev_data = data[(data.new_industry_name == new_index) 
                            & (data.minor_industry_name == minor_index)]
            title = new_index + minor_index + ' '

        elif (new_index != '') & (minor_index == ''):
            rev_data = data[(data.new_industry_name == new_index)]
            title = new_index + ' '

        elif (new_index == '') & (minor_index != ''):
            rev_data = data[(data.minor_industry_name == minor_index)]
            title = minor_index + ' '
        rev_data = rev_data.groupby('rev_period', as_index=False).agg({'rev':'sum'}).reset_index(drop=True)
        rev_data = fn.get_st_mom_yoy(rev_data)
rev_predict = get_predict(rev_data)
rev_predict
# 繪圖
#     REV = fn.get_revpic(rev_data, rev_predict, (title + ' 各年度月營收'))
# MOM = fn.get_mompic(rev_data, rev_predict, (title + ' 各年度月營收'))
