from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
from scipy import stats
import views.all_function as fn

from server import app


latest_data = pd.read_csv('/Users/yuchun/Revenue/Web2/models/2023/01最新營收公布.csv')

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
            sort_action="native",
            sort_mode='single',
            # page_action='custom',
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
        )
    ], style={
        'padding': '2rem 2rem',
        'font-family': '"Open Sans", sans-serif'
    })

