import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
import numpy as np
from Upload_git import upload

df = pd.read_csv('db.csv', low_memory=False)
df
revenue = pd.read_excel('1217_營收.xlsx', sheet_name='RUN1')

stock_info = revenue.iloc[:, 0:3].dropna().rename(
    {'公司簡稱':'company', 'TSE新產業名':'new_name', 'TEJ子產業名':'minor_name'}, axis=1)
stock_info['st_code'] = stock_info.company.str[0:4]
stock_info['st_name'] = stock_info.company.str[5:]
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()

"""
選擇
"""
dropdown = new_industry_name[0]
st_input = '2330'
year = [2018, 2023]

# 
years = [str(year[0]),str(year[1])]




upload.execute('Update_file')
# pd.read_csv('db.csv', low_memory=False)