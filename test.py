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

# write a df to a PostgreSQL database
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine(
    'postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)
df = pd.read_sql('tej_revenue', engine);df

# df = pd.read_csv('db.csv', low_memory=False)
revenue = pd.read_excel('1217_營收.xlsx', sheet_name='RUN1')
revenue = pd.read_sql('industry', engine)
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()

"""
選擇
"""
dropdown = new_industry_name[0]
dropdown
st_input = '2330'

year = [2018, 2023]

# 
years = [str(year[0]),str(year[1])]




upload.execute('Update_file')
# pd.read_csv('db.csv', low_memory=False)