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
# from Upload_git import upload
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine
import revenue_function as fn


"""""""""
connect to db
"""""""""
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
        html.H3(id='header', children=["雋寬資訊"], style={'color':'black'})
    ],style={"padding": "2rem 2rem"}
)


# 產業年度營收
new_dropdown = dcc.Dropdown(
    id='new-dropdown-component',
    options=new_industry_name,
    clearable=False,
    value=new_industry_name[0]
)

minor_dropdown = dcc.Dropdown(
    id='minor-dropdown-component',
    options=minor_industry_name,
    clearable=False,
    value=minor_industry_name[0]
)

satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=[html.Br(), " 上市櫃產業年度合併報表"]
)

new_title = html.H5(id="new-name", children=["選擇 TEJ 產業分類"])

minor_title = html.H5(id="minor-name", children=["選擇 TEJ 子產業分類"])

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=[""]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        # html.Img(src=app.get_asset_url("logo.png"), style={"width":"5rem", "height":"3rem"}),
        satellite_dropdown_text,
        html.Div(id="panel-side-text", children=new_title),
        html.Div(id="new-dropdown", children=new_dropdown),
        html.Br(),
        html.Div(children=minor_title), 
        html.Div(id="minor-dropdown", children=minor_dropdown),
        html.Br(),
        html.H1("輸入股號或公司名稱查詢", style={"font-size": "1rem", "letter-spacing": "0.1rem", "color": "#787878", "text-align": "center"}),
        html.Div(dcc.Input(placeholder="輸入...", id='st_input', type='text', style={"color":"black", "font-size":"12px", "width":"20rem", "height":"2rem"})),
        html.Br(),
        html.Div(
            html.Button("送出查詢",
                        id='submit',
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


"""
Main Panel
"""
rank_col = ['公司代碼', '公司簡稱', '最新公告日期', '營收', 'MOM%', 'YOY%']
rank = html.Div([
    html.P("同產業合併月營收排名", 
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }),
    html.Div([
        dash_table.DataTable(
            id='rank_table',
            columns=[{"name": i, "id": i, "deletable": True} for i in (rank_col)],
            page_current=0,
            page_size=10,
            # page_action='custom',
            sort_action='custom',
            sort_mode='single',
            sort_by=[],
            style_cell={
                'font_size': '16px',
                'overflow':'hidden',
                'textOverflow':'ellipsis',
                'color':'black', 
                "flex": "5 83%",
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': i},
                    'textAlign': 'left'
                } for i in ['公司代碼', '公司簡稱', '最新公告月份']
            ]
        )], 
        className="dbc-row-selectable",
    )
], style={'width':'100%', 'overflowX': 'scroll'})


table_col = ['Year'] + ["%.2d" % i for i in range(1, 13)]
table = html.Div([
    html.P("各年度月營收",
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
    html.Div(
        dash_table.DataTable(
            id='rev_table',
            columns=[{"name": i, "id": i, "deletable": True} for i in (table_col)],
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
            export_format="xlsx",
            export_headers="display",
        ),
        className="dbc-row-selectable",
    )
], style={'width':'100%', 'overflowX': 'scroll'})


main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        rank,
        html.Br(), 
        table,
        html.Br(),
        html.Div([
            dcc.Graph(id='graph_rev'),
            dcc.Graph(id='graph_mom'),
            dcc.Graph(id='graph_yoy')
        ], style={"flex-direction": "row"})
    ],
    style={"flex-direction": "column", 
           "flex": "5 83%",
           "padding": "2.5rem 1rem",
           "display":"flex",
           "width":'60%'
           }
)

# Root
root_layout = html.Div(
    id="root",
    children=[
        side_panel_layout,
        main_panel_layout
    ],
)

tab1 = dbc.Tab(label="上市櫃產業年度合併報表", tab_id="tab-1", children=root_layout)
tab2 = dbc.Tab(label="營收即時更新資訊", tab_id="tab-2")
tab3 = dbc.Tab(label="ETF價差套利資訊", tab_id="tab-3")
tabs = dbc.Tabs([tab1, tab2, tab3])


app.layout = html.Div(
    [
        header,
        tabs
    ],
    style={"padding": "2rem 4rem"}
)



"""
callback
"""
@app.callback(
    [Output('rev_table', 'data'),
     Output('rank_table', 'data'),
     Output("graph_rev", "figure"),
     Output("graph_mom", "figure"),
     Output("graph_yoy", "figure")],

    [Input('submit', 'n_clicks'),
     State("new-dropdown-component", "value"),
     State("minor-dropdown-component", "value"),
     State("st_input", "value")],
    prevent_initial_call=True
)
def update_table(submit, dropdown1, dropdown2, st_input):
    if st_input is None or st_input == '':
        try:
            if (dropdown1 != new_industry_name[0]) and (dropdown2 == minor_industry_name[0]):
                mask = ("new_industry_name = '" + dropdown1 + "'")

            elif (dropdown2 != minor_industry_name[0]) and (dropdown1 == new_industry_name[0]):
                mask = ("minor_industry_name = '" + dropdown2 + "'")

            elif (dropdown1 != new_industry_name[0]) and (dropdown2 != minor_industry_name[0]):
                mask = ("new_industry_name = '" + dropdown1 + "' and " + "minor_industry_name = '" + dropdown2 + "'")

            # 從 db 撈資料
            st_search = """
            select st_code, st_name, rev_period, declaration_date, rev
            from tej_revenue
            where {};
            """.format(mask)

            data = pd.read_sql(st_search, engine)
            data = data.groupby(by='st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True,inplace=False)
            
            # 產業最新營收公布情形
            latest = fn.get_latest(data)

            # 產業總營收狀況
            data = data.groupby(by='rev_period', as_index=False).agg({'rev': 'sum'})
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
            table = table.to_dict('records')
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
            data = data.groupby(by='st_code', as_index=False).apply(fn.get_st_mom_yoy).reset_index(drop=True,
                                                                                                   inplace=False)

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
            table = table.to_dict('records')
            return table, latest, REV, MOM, YOY
        
        except IndexError:
            print('跳警示通知：查無該股票營收，請重新輸入，並reset')


if __name__ == '__main__':
    app.run_server(port=8050, debug=True)
