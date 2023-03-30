from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc
import dash_daq as daq
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


latest_data = pd.read_csv('/Users/yuchun/Revenue/Web2/models/最新營收公布.csv')
cb = pd.read_pickle('/Users/yuchun/Revenue/Web2/models/cb.pkl')
st_futures = pd.read_pickle('/Users/yuchun/Revenue/Web2/models/st_futures.pkl')
filtered = pd.read_pickle('/Users/yuchun/Revenue/Web2/models/filtered.pkl')


switches = html.Div([
    html.Div([html.P(['濾掉特定產業'],style={'font_size': '1rem', "color": "#787878"})]),
    html.Br(),
    html.Div([daq.BooleanSwitch(id='filtered-boolean-switch', on=False,color="#fec036")]),
    html.Div([html.P(['有發個股期'],style={'font_size': '1rem', "color": "#787878"})]),
    html.Div([daq.BooleanSwitch(id='st_futures-boolean-switch',on=False,color="#fec036")]), 
    html.Div([html.P(['有發可轉債CB'],style={'font_size': '1rem', "color": "#787878"})]),
    html.Div([daq.BooleanSwitch(id='cb-boolean-switch',on=False,color="#fec036")])
    ],
    style={
        'display': 'flex',
        'flex-direction': 'row', 
        'flex-wrap': 'wrap',
        }
)


latest_revenue_page = html.Div([
    html.H1([html.Br(), "最新公告營收"],
           style={
               "font-size": "2rem", 
               "color": "#787878"
            #    "font-size": "1.5rem", 
            #    "letter-spacing": "0.1rem", 
            #    "color": "black", 
            #    "text-align": "left"
               }
           ),
    switches, 
    html.Div(
        dash_table.DataTable(
            id='latest_revenue_table',
            columns=[
                {"name": i, "id": i, "selectable": True} for i in latest_data.columns
            ],
            data = latest_data.to_dict('records'),
            sort_action="native",
            sort_mode='single',
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
        'flex-direction': 'column',
        'font-family': '"Open Sans", sans-serif'
    })



"""
Callback
"""
@app.callback(
    Output('latest_revenue_table', 'data'),
    [Input('cb-boolean-switch', 'on'),
     Input('st_futures-boolean-switch', 'on'),
     Input('filtered-boolean-switch', 'on')]
)
def latest_revenue_switch_chart(cb_switch, st_futures_switch, filtered_switch):
    if cb_switch == True:
        cb_option = (latest_data['代號'].astype(str).isin(cb))
    else:
        cb_option = (latest_data['代號'].isin(latest_data['代號']))
    if st_futures_switch == True:
        st_futures_option = (latest_data['代號'].astype(str).isin(st_futures))
    else:
        st_futures_option = (latest_data['代號'].isin(latest_data['代號']))

    if filtered_switch == True:
        filtered_option = (latest_data['代號'].astype(str).isin(filtered))
    else:
        filtered_option = (latest_data['代號'].isin(latest_data['代號']))

    return latest_data[cb_option & st_futures_option & filtered_option].sort_values('yoy％', ascending=False).to_dict('records')        