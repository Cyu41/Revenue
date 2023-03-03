import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import pickle
import urllib.request
import ssl
import certifi
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine


cluster = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/cluster_industry.csv')
industry = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/industry.csv')
daily_trading = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/daily_trading.csv', low_memory=False)
def latest_return(data):
    data['近一日漲跌%'] = round(data.Close.pct_change(1), 4)
    data['近一週漲跌%'] = round(data.Close.pct_change(5), 4)
    data['近一月漲跌%'] = round(data.Close.pct_change(20), 4)
    return data

"""
app layout
"""
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

server = app.server

header = html.Div(
    [
        html.Br(),
        html.Img(src=app.get_asset_url("logo.png"), style={"width":"5rem", "height":"3rem"}),
        html.Br(),
        html.H3(id='header', children=["小飛鷹"], style={'color':'black'})
    ],style={"padding": "2rem 2rem"}
)


tab1 = dbc.Tab(label="上市櫃產業年度合併報表", tab_id="tab-1")
tab2 = dbc.Tab(label="營收獲利預估", tab_id="tab-2")#, children=latest_rev)
tab3 = dbc.Tab(label="台股分類", tab_id="tab-3")
tabs = dbc.Tabs([tab1, tab2, tab3])


app.layout = html.Div(
    [
        header,
        tabs
    ],
    style={"padding": "2rem 4rem"}
)







"""
Call back
"""




if __name__ == '__main__':
    app.run_server(port=8040, debug=True)
    
    
    