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
import views.all_function as fn

from server import app

"""
Import data
"""
cluster = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/cluster_industry.csv')
industry = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/industry.csv')
daily_trading = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/daily_trading.csv', low_memory=False).drop('Unnamed: 0', axis=1)
group = pd.merge(industry, cluster.loc[:, ['歆凱分組', '代號']], on='代號', how='left').drop('Unnamed: 0', axis=1)



stock_panel_layout = html.Div(
    id="cluster_panel-side",
    children=[
        html.H1(
            id="cluster-text", 
            children=[html.Br(), "機器學習台股分類"], 
            style={
                "font-size": "2rem", 
                "color": "#787878"
                }
            )
        ,
        html.P("輸入股號", style={"font-size": "1.2rem", "letter-spacing": "0.1rem", "color": "black", "text-align": "left"}),
        html.Div(dcc.Input(placeholder="輸入...", id='cluster_input', type='text', style={"color":"black", "font-size":"1.2rem", "width":"15rem", "height":"1.5rem"})),
        html.Br(),
        html.Div(
            html.Button("送出查詢",
                        id='cluster_submit',
                        n_clicks=0, 
                        style={
                            "color":"#fec036",
                            "font-size":"15px", 
                            "width":"10rem", 
                            "height":"2rem"
                            }
                        )
            )
    ],
)


group_table_col = ['date','近一日漲跌％','近一週漲跌％','近一月漲跌％']
group_table = html.Div([
    html.P("概念股整體走勢",
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


cluster_table_col = ['代號','名稱','近一日漲跌％','近一週漲跌％','近一月漲跌％']
all_cluster_table = html.Div([
    html.P("概念股個別報酬走勢",
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.2rem", 
               "color": "black", 
               "text-align": "left",
               'font-family': '"Open Sans", sans-serif'
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
        html.Div([dcc.Graph(id='graph_cluster')], style={"flex-direction": "row"}),
        html.Br(),
        all_cluster_table,
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
        'padding': '3rem 3rem',
        'overflowX': 'scroll',
        'font-family': '"Open Sans", sans-serif'
        }
)


"""
callback
"""
@app.callback(
    [Output('cluster_group_table', 'data'),
     Output("cluster_table", "data"),
     Output("graph_cluster", "figure")
     ],
    [Input('cluster_submit', 'n_clicks'),
     State("cluster_input", "value")],
    prevent_initial_call=True
)
def update_table(submit, st_input):
    lookup = np.where(st_input.isnumeric() == True, '代號', '名稱')
    group_num = group[group[lookup].astype(str) == st_input]['歆凱分組'].values[0]

    if np.isnan(group_num) == True:
        group_num = group[group[lookup].astype(str) == st_input]['industry_title'].values[0]
        group_data = group[group['industry_title'] == group_num]
        group_title = 'ML並無分類，在TEJ為 '+['、'.join(group_data.new_industry.drop_duplicates().to_list())][0] + ' 概念股報酬走勢'

    else:
        group_data = group[group['歆凱分組'] == group_num]
        group_title = 'TEJ為 '+['、'.join(group_data.new_industry.drop_duplicates().to_list())][0] + ' 概念股報酬走勢'


    df = daily_trading[daily_trading.st_code.isin(group_data['代號'].astype(str))]
    df = df.groupby('st_code', as_index=False).apply(fn.latest_return)

    latest = df.loc[:, ['st_code', 'st_name', '近一日漲跌％','近一週漲跌％','近一月漲跌％']].drop_duplicates('st_code', keep='last')
    latest = latest.rename({'st_code':'代號', 'st_name':'名稱'}, axis=1)
    group_return = df.groupby('date', as_index=False).agg({'近一日漲跌％':'mean', '近一週漲跌％':'mean', '近一月漲跌％':'mean'})
    group_return_latest = group_return.tail(1)

    group_return['近一日漲跌％'] = group_return['近一日漲跌％'].cumsum()
    mask = group_return['近一日漲跌％'] >= 0
    group_return['ret_above'] = np.where(mask, group_return['近一日漲跌％'], 0)
    group_return['ret_below'] = np.where(mask, 0, group_return['近一日漲跌％'])

    fig = go.Figure(go.Scatter(
        y=group_return['ret_above'],
        x=group_return.date, 
        fill='tozeroy',
        fillcolor='rgba(240, 128, 128, 0.5)',
        opacity=0.5, 
        mode='none',
        text=group_return['近一日漲跌％']))

    fig.add_trace(go.Scatter(
        y=group_return['ret_below'],
        x=group_return.date, 
        fill='tozeroy',
        fillcolor='rgba(26,150,65,0.5)',
        opacity=0.5, 
        mode='none',
        text=group_return['近一日漲跌％']))

    fig.update_xaxes(
        showspikes=True, 
        spikecolor="rgb(204, 204, 204)", 
        spikemode="across", 
        spikethickness=0.1
        )

    fig.update_layout(
    #     hovermode='x',
        title = group_title,
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgb(204, 204, 204)',
            gridcolor='rgb(204, 204, 204)',
            showline=False,
            showticklabels=True,
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=False,
        plot_bgcolor='white'

    )
    fig.update_xaxes(title='日期')
    return group_return_latest.to_dict('records'), latest.to_dict('records'), fig