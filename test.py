import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
import numpy as np
from Upload_git import upload
from os import system
# import time
from time import ctime, sleep
from Upload_git import upload
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
import revenue_function as fn
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc

"""
connect to db
"""
host='database-1.cyn7ldoposru.us-east-1.rds.amazonaws.com'
port='5432'
user='Yu'
password='m#WA12J#'
database="JQC_Revenue1"

engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        user, password, host, port, database), echo=True)

stock_info = pd.read_csv('stock_info.csv')
stock_info.st_code = stock_info.st_code.astype(str)

"""
callback input & output detail 
"""
revenue = pd.read_sql('industry', engine)
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()

"""
layout of app
"""
dbc_css = "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server

# Side panel
satellite_dropdown = dcc.Dropdown(
    id='satellite-dropdown-component',
    options=new_industry_name,
    clearable=False,
    value=new_industry_name[0]
)

minor_dropdown = dcc.Dropdown(
    id='minor-dropdown-component',
    options=minor_industry_name,
    clearable=False,
    value=minor_industry_name[0])

satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=[html.Br(), " 上市櫃產業年度合併報表"]
)
satellite_title = html.H5(id="satellite-name", children=["選擇 TEJ 產業分類"])
minor_title = html.H5(id="minor-name", children=["選擇 TEJ 子產業分類"])

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=[""]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        html.Img(src=app.get_asset_url("logo.png"), style={"width":"5rem", "height":"3rem"}),
        satellite_dropdown_text,
        html.Div(id="panel-side-text", children=satellite_title),
        html.Div(id="satellite-dropdown", children=satellite_dropdown),
        html.Br(),
        html.Div(children=minor_title),
        html.Div(id="minor-dropdown", children=minor_dropdown),
        html.Br(),
        html.H1("輸入股號或公司名稱查詢", style={"font-size": "1rem", "letter-spacing": "0.1rem", "color": "#787878", "text-align": "center"}),
        html.Div(dcc.Input(placeholder="輸入...", id='stock_code', type='text', style={"color":"black", "font-size":"12px", "width":"20rem", "height":"1.5rem"})),
        html.Br(),
        html.Div(html.Button("送出查詢",id='submit',n_clicks=0, style={"color":"#fec036","font-size":"15px", "width":"10rem", "height":"2rem"}))
    ],
)


"""
Main Panel
"""
rank_col = ['排名', '公司代碼', '公司簡稱', '最新公告月份', '營收', 'MOM%', 'YOY%']

rank = html.Div([
    html.P("同產業合併月營收排名"),
    html.Div(
        dash_table.DataTable(
            id='rank_table',
            columns=[{"name": i, "id": i, "deletable": True} for i in (rank_col)],
            page_current=0,
            page_size=5,
            # page_action='custom',
            sort_action='custom',
            sort_mode='single',
            sort_by=[],
            style_cell={
                'font_size': '16px',
                'overflow':'hidden',
                'textOverflow':'ellipsis',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': i},
                    'textAlign': 'left'
                } for i in ['公司代碼', '公司簡稱', '最新公告月份']
            ]
        ),
        className="dbc-row-selectable",
    )
])

map_graph = html.Div(
    id="world-map-wrapper",
    children=[
        dcc.Graph(id="world-map"),
        rank
    ],
)


histogram = html.Div(
    id="histogram-container",
    children=[
        html.Div(
            id="histogram-header",
            children=[
                html.H1(
                    id="histogram-title", children=["各年度月營收 MoM% / YoY%"]
                ),
            ],
        ),
        dcc.Graph(id='graph_mom'),
        dcc.Graph(id='graph_yoy')
    ],
)


main_panel_layout = html.Div(
    id="panel",
    children=[
        dcc.Interval(id="interval", interval=1 * 2000, n_intervals=0),
        map_graph,
        histogram
    ],
)

# Root
root_layout = html.Div(
    id="root",
    children=[
        side_panel_layout,
        main_panel_layout
    ],
)

app.layout = root_layout

    
"""
callback
"""
@app.callback(
    [Output('rev_table', 'data'),
     Output('rank', 'data'),
     Output("graph_rev", "figure"),
     Output("graph_mom", "figure"),
     Output("graph_yoy", "figure")],
    
    [Input('submit', 'n_clicks'),
     State("satellite_dropdown", "value"),
     State("satellite_dropdown", "value"),
     State("st_input", "value")],
    prevent_initial_call=True
) 
def update_table(submit, dropdown1, dropdown2, st_input):
    if st_input is None or st_input == '':
        try:
            if dropdown1 is not None and dropdown2 is None or dropdown2 == '':
                mask = ("new_industry_name = '" + dropdown1 + "'")
                
            elif dropdown1 is None and dropdown2 is not None or dropdown1 == '':
                mask = ("minor_industry_name = '" + dropdown2 + "'")
                
            elif dropdown1 is not None and dropdown2 is not None:
                mask = ("new_industry_name = '" + dropdown1 + "' and " + "minor_industry_name = '" + dropdown2 + "'")
                
            # 從 db 撈資料
            st_search = """
            select st_code, st_name, rev_period, declaration_date, rev
            from tej_revenue 
            where {};
            """.format(mask)
            
            data = pd.read_sql(st_search, engine)
            data = data.groupby(by='st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True, inplace=False)

            # 產業最新營收公布情形
            latest = fn.get_latest(data)
            
            # 產業總營收狀況
            data = data.groupby(by='rev_period', as_index=False).agg({'rev':'sum'})
            data = fn.get_st_mom_yoy(data)

            # 預測資料
            data_predict = fn.predict(data)
            
            # 繪圖
            title = dropdown1 + ' '
            REV = fn.get_revpic(data, data_predict, (title + ' 各年度月營收'))
            MOM = fn.get_mompic(data, data_predict, (title + ' 各年度月營收'))
            YOY = fn.get_yoypic(data, data_predict, (title + ' 各年度月營收'))
            
            # 整理營收資訊表
            table = data.pivot_table(values='rev', index='Year', columns='month').reset_index()
            data_predict.Year = data_predict.Year + str(' 預估值')
            table = pd.concat([table, data_predict.tail(12).pivot_table(index='Year', columns='month', values='rev').reset_index()],axis=0)
            return table, latest, REV, MOM, YOY
        except KeyError:
            print("跳警示通知：該分類沒有相關個股，請重新選擇，並reset")
            
            
    else:
        try:
            if (st_input.isdigit() == True):
                industry = stock_info[stock_info.st_code == st_input].new_industry_name.values[0]
                mask = ("new_industry_name = '" + industry + "'")
                st_mask = 'st_code'

            else:
                industry = stock_info[stock_info.st_name == st_input].new_industry_name.values[0]
                mask = ("new_industry_name = '" + industry + "'")
                st_mask = 'st_name'

            # 從 db 撈資料
            st_search = """
            select st_code, st_name, rev_period, declaration_date, rev
            from tej_revenue 
            where {}; 
            """.format(mask)
            data = pd.read_sql(st_search, engine)
            data = data.groupby(by='st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True, inplace=False)

            # 產業最新營收公布情形
            latest = fn.get_latest(data)
            
            # 轉換成個股總營收
            data = data[data[st_mask] == st_input]
            data = fn.get_st_mom_yoy(data)
            
            # 預測資料
            data_predict = fn.predict(data)
            
            # 繪圖
            title = data.st_code[0] + ' ' + data.st_name[0]
            REV = fn.get_revpic(data, data_predict, (title + ' 各年度月營收'))
            MOM = fn.get_mompic(data, data_predict, (title + ' 各年度月營收'))
            YOY = fn.get_yoypic(data, data_predict, (title + ' 各年度月營收'))   
            
            # 整理營收資訊表
            table = data.pivot_table(values='rev', index='Year', columns='month').reset_index()
            data_predict.Year = data_predict.Year + str(' 預估值')
            table = pd.concat([table, data_predict.tail(12).pivot_table(index='Year', columns='month', values='rev').reset_index()],axis=0)
            return table, latest, REV, MOM, YOY
        except IndexError:
            print('跳警示通知：查無該股票營收，請重新輸入，並reset')








if __name__ == '__main__':
    app.run_server(port=8000, debug=True)
