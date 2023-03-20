from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_html_components as html 
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
from scipy import stats


def get_yoy(data):
    data = data.sort_values('Year')
    data['yoy'] = round(data.rev.diff()/data.rev.shift(1), 4)
    return data


def get_st_mom_yoy(data):
    data['Year'] =  data.rev_period.astype(str).str[0:4]
    data['month'] = data.rev_period.astype(str).str[5:7]
    data['mom'] = round(data.rev.diff()/data.rev.shift(1), 4)
    yoy = pd.DataFrame()
    yoy = data.groupby('month').apply(get_yoy).reset_index(drop=True, inplace=False)
    return yoy[yoy.Year >= '2016']


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

update = pd.read_excel("/Users/yuchun/Revenue/2022月營收更新報表_yuchun.xlsm", sheet_name='工作表1', header=6,
                       usecols=[3,4], names=['name', 'rev_period'])
update['rev_period'] = pd.to_datetime(update['rev_period'], format='%Y%m').dt.strftime('%Y/%m')

latest = update.rev_period.head(1).values[0]
latest_data = db.groupby('st_code', as_index=False).apply(get_st_mom_yoy).reset_index(drop=True)
latest_data = latest_data.loc[:, ['st_code', 'st_name', 'rev_period', 'rev', 'mom', 'yoy']]
latest_data = latest_data[latest_data.rev_period == latest]


latest_revenue_page = html.Div([
    html.P("最新公告營收",
           style={
               "font-size": "1.5rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
    html.Div(
        dash_table.DataTable(
            columns=[
                {"name": i, "id": i, "selectable": True} for i in latest_data.columns
            ],
            data = latest_data.to_dict('records'),
            sort_action="custom",
            sort_mode='single',
            page_action='custom',
            page_current= 0,
            page_size = 20,
            style_cell={
                'font_size': '16px',
                'overflow':'hidden',
                'textOverflow':'ellipsis',
                'color':'black',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'Year'},
                    'textAlign': 'left'
                }
            ],
            export_format="xlsx",
            export_headers="display",
        ),
        className="dbc-row-selectable",
        style={
            'display': 'flex',
            'padding': '1rem 1rem',
            'fontFamily': 'Open Sans, sans-serif',
            'flex-direction': 'row',
            'justify-content': 'stretch'
            },
        )
    ], style={
        "flex-direction": "row", 
        'width':'100%', 
        'padding': '4rem 4rem',
        'overflowX': 'scroll',
        'fontFamily': 'Open Sans'
        }
    )

