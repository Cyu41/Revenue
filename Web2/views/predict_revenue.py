import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_daq as daq
import pandas as pd
import plotly.express as px
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
from scipy import stats
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import views.all_function as fn

from server import app


predict_data = pd.read_csv('/Users/yuchun/Revenue/Predict_REV/2023/03營收預估.csv')


predict_table_col = ['代號', '名稱', '預估月', 'yoy', 'mom', '預估營收（百萬）', 'TEJ產業']
predict_revenue_page = html.Div([
    html.Div([
        html.H1("次月營收預估",
           style={
               "font-size": "2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
        daq.BooleanSwitch(
            id='predict-boolean-switch',
            on=False,
            label="濾掉特定產業",
            labelPosition="top",
            color="#fec036",
            style={'font_size': '1rem', "color": "#787878"}
            ),
    ]),
    html.Div(
        dash_table.DataTable(
            id='predict_table',
            data = predict_data.to_dict('records'),
            columns=[{"name": i, "id": i} for i in (predict_table_col)],
            page_current=0,
            page_size=20,
            sort_action="native",
            sort_mode='single',
            # page_action='custom',
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
        "flex-direction": "row", 
        'width':'100%', 
        'padding': '4rem 4rem',
        'overflowX': 'scroll',
        'font-family': '"Open Sans", sans-serif'
        }
    )


@app.callback(
    Output('predict_table', 'data'),
    Input('predict-boolean-switch', 'on'),
)
def statistics_switch_chart(on):
    if on:
        table = predict_data[(predict_data['TEJ產業'] != 'M1722 生技醫療') 
                             & (predict_data['TEJ產業'] != 'M2326 光電業')
                             & (predict_data['TEJ產業'] != 'M2331 其他電子業') 
                             & (predict_data['TEJ產業'] != 'M2500 建材營造') 
                             & (predict_data['TEJ產業'] != 'M2600 航運業') 
                             & (predict_data['TEJ產業'] != 'M2800 金融業')
                             & (predict_data['TEJ產業'] != 'M2900 貿易百貨')
                             & (predict_data['TEJ產業'] != 'M3200 文化創意業')]
        return table.to_dict('records')
    
    else:
        table = predict_data
        return table.to_dict('records')
