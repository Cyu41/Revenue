import dash_html_components as html
import dash_core_components as dcc
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

from server import app


predict_data = pd.read_csv('/Users/yuchun/Revenue/Predict_REV/2023/03營收預估.csv')
predict_data = predict_data[predict_data.yoy <= 1000000000].sort_values('yoy', ascending=False)

predict_data_futures = pd.read_csv('/Users/yuchun/Revenue/Predict_REV/2023/03營收預估(個股期).csv')
predict_data_futures = predict_data_futures[predict_data_futures.yoy <= 1000000000].sort_values('yoy', ascending=False)


predict_table_col = ['代號', '名稱', 'yoy', 'mpm', '預估營收（百萬）', 'TEJ產業']
predict_revenue_page = html.Div([
    html.Div([
        html.P("次月營收估季",
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
        daq.BooleanSwitch(
            id='predict-futures-boolean-switch',
            on=False,
            label="濾掉特定產業",
            labelPosition="top",
            color="#fec036",
            ),
    ]),
    html.Div(
        dash_table.DataTable(
            id='predict_table',
            columns=[{"name": i, "id": i} for i in (predict_table_col)],
            page_current=0,
            page_size=20,
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
        'width':'100%', 
        'padding': '4rem 4rem',
        "flex-direction": "row", 
        'overflowX': 'scroll',
        'font-family': 'Open Sans'
        })


# predict_revenue_page = html.Div([
#     html.P("次月營收預估",
#            style={
#                "font-size": "1.5rem", 
#                "letter-spacing": "0.1rem", 
#                "color": "black", 
#                "text-align": "left"
#                }
#            ),
#     html.Div(
#         dash_table.DataTable(
#             id='predict-table',
#             columns=[
#                 {"name": i, "id": i, "selectable": True} for i in predict_data.columns
#             ],
#             data = predict_data.to_dict('records'),
#             sort_action="custom",
#             sort_mode='single',
#             page_action='custom',
#             page_current= 0,
#             page_size = 20,
#             style_cell={
#                 'font_size': '16px',
#                 'overflow':'hidden',
#                 'textOverflow':'ellipsis',
#                 'color':'black',
#             },
#             style_cell_conditional=[
#                 {
#                     'if': {'column_id': 'Year'},
#                     'textAlign': 'left'
#                 }
#             ],
#             export_format="xlsx",
#             export_headers="display",
#         ),
#         className="dbc-row-selectable",
#         )
#     ],    style={
#         "flex-direction": "row", 
#         'width':'100%', 
#         'padding': '4rem 4rem',
#         'overflowX': 'scroll',
#         'font-family': 'Open Sans'
#         })



@app.callback(
    Output('predict_table', 'data'),
    Input('predict-boolean-switch', 'on'),
)
def statistics_switch_chart(switch):
    if switch == False:
        table = predict_data
        return table.to_dict('records')
    
    elif switch == True:
        table = predict_data[(predict_data.new_industry_name != 'M1722 生技醫療') 
                             & (predict_data.new_industry_name != 'M2326 光電業')
                             & (predict_data.new_industry_name != 'M2331 其他電子業') 
                             & (predict_data.new_industry_name != 'M2500 建材營造') 
                             & (predict_data.new_industry_name != 'M2600 航運業') 
                             & (predict_data.new_industry_name != 'M2800 金融業')
                             & (predict_data.new_industry_name != 'M2900 貿易百貨')
                             & (predict_data.new_industry_name != 'M3200 文化創意業')
                             & (predict_data.minor_industry_name != 'M25A 建設')]
        return table.to_dict('records')
