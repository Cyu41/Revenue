import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
import dash


stock_panel_layout = html.Div(
    id="cluster_panel-side",
    children=[
        html.H3(id="cluster-text", children=[html.Br(), "機器學習台股分類"], style={"color": "#787878"}),
        html.H1("輸入股號", style={"font-size": "1rem", "letter-spacing": "0.1rem", "color": "#787878", "text-align": "left"}),
        html.Div(dcc.Input(placeholder="輸入...", id='cluster_input', type='text', style={"color":"black", "font-size":"12px", "width":"15rem", "height":"1.8rem"})),
        html.Div(
            html.Button("送出查詢",
                        id='cluster_submit',
                        n_clicks=0, 
                        style={
                            "color":"#fec036",
                            "font-size":"15px", 
                            "fontFamily":'Open Sans',
                            "width":"10rem", 
                            "height":"1.5rem"
                            }
                        )
            )
    ],
)


group_table_col = ['date','近一日漲跌％','近一週漲跌％','近一月漲跌％']
group_table = html.Div([
    html.P("概念股報酬走勢",
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
    html.Div(
        dash_table.DataTable(
            id='cluster_group_table',
            columns=[{"name": i, "id": i} for i in (group_table_col)],
            page_current=0,
            page_size=10,
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
        ),
        className="dbc-row-selectable",
    )
], style={"flex-direction": "row", 'width':'100%', 'overflowX': 'scroll'})


cluster_table_col = ['st_code','st_name','近一日漲跌％','近一週漲跌％','近一月漲跌％']
all_cluster_table = html.Div([
    html.P("概念股報酬走勢",
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
    html.Div(
        dash_table.DataTable(
            id='cluster_table',
            columns=[{"name": i, "id": i} for i in (cluster_table_col)],
            page_current=0,
            page_size=10,
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
        ),
        className="dbc-row-selectable",
    )
], style={"flex-direction": "row", 'width':'100%', 'overflowX': 'scroll'})


stock_main_panel_layout = html.Div(
    id="cluster_panel-upper-lower",
    children=[
        group_table,
        html.Br(),
        all_cluster_table,
        html.Br(),
        html.Div([dcc.Graph(id='graph_cluster')], style={"flex-direction": "row"})
        ],
    style={
        "flex-direction": "column", 
        "display":"flex",
        "width":'100%'
        }
)

ml_cluster_page = html.Div(
    id="cluster_root",
    children=[
        stock_panel_layout,
        stock_main_panel_layout
    ],
    style={
        "flex-direction": "row", 
        'width':'100%', 
        'padding': '4rem 4rem',
        'overflowX': 'scroll',
        'fontFamily': 'Open Sans'
        }
)
