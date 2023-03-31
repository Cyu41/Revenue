import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import views.all_function as fn
from sqlalchemy import create_engine
import pandas as pd

from server import app

"""
import revenue data
"""
db = pd.read_pickle('/Users/yuchun/Revenue/Web2/models/營收db.pkl')
industry = pd.read_pickle('/Users/yuchun/Revenue/Web2/models/industry.pkl')
predict = pd.read_csv('/Users/yuchun/Revenue/Web2/models/營收預估.csv')
order = predict.columns.to_list()
exchange_industry_name = pd.Series('~~請選擇 交易所 產業分類~~')
tej_industry_name = pd.Series('~~請選擇 TEJ 產業分類~~')
exchange_industry_name = pd.concat([exchange_industry_name, 
                                    industry['交易所產業分類'].drop_duplicates().sort_values()], 
                                   axis=0).reset_index(drop=True)
tej_industry_name = pd.concat([tej_industry_name, 
                                    industry['TEJ產業分類'].drop_duplicates().sort_values()], 
                                   axis=0).reset_index(drop=True)


# 產業年度營收
new_dropdown = dcc.Dropdown(
    id='new-dropdown-component',
    options=exchange_industry_name,
    clearable=False,
    value=exchange_industry_name[0]
)

minor_dropdown = dcc.Dropdown(
    id='minor-dropdown-component',
    options=tej_industry_name,
    clearable=False,
    value=tej_industry_name[0]
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
        satellite_dropdown_text,
        html.Div(id="panel-side-text", children=new_title),
        html.Div(id="new-dropdown", children=new_dropdown),
        html.Div(children=minor_title), 
        html.Div(id="minor-dropdown", children=minor_dropdown),
        html.H5("輸入股號或公司名稱查詢", style={"font-size": "1rem", "letter-spacing": "0.1rem", "color": "#787878", "text-align": "center"}),
        html.Div(dcc.Input(placeholder="輸入...", id='st_input', type='text', style={"color":"black", "font-size":"15px", "width":"20rem", "height":"2rem"})),
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
    ]
)


"""
Main Panel
"""
table_col = ['年份'] + ["%.2d" % i for i in range(1, 13)]
table = html.Div([
    html.P("各年度月營收", 
           id='rev_search_title',
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


rank_col = ['代號', '名稱', 'rev_period', '營收(百萬)', 'yoy％', 'mom％', '預估次月yoy％','預估次月mom％']
revenue_rank = html.Div([
    html.P("同產業個股營收狀況", 
           id='rank_title',
           style={
               "font-size": "1.2rem", 
               "letter-spacing": "0.1rem", 
               "color": "black", 
               "text-align": "left"
               }
           ),
    html.Div(
        dash_table.DataTable(
            id='rank_rev_table',
            columns=[{"name": i, "id": i} for i in (rank_col)],
            page_current=0,
            page_size=10,
            sort_action="native",
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
], style={'width':'100%', 'overflowX': 'scroll'})
    



main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        revenue_rank,
        html.Br(), 
        html.Div([
            dcc.Graph(id='graph_rev'),
            dcc.Graph(id='graph_mom'),
            dcc.Graph(id='graph_yoy')
        ], style={"flex-direction": "row"}),
        html.Br(),
        table        
    ],
)


industry_revenue_page = html.Div(
    id="root",
    children=[
        side_panel_layout,
        main_panel_layout
    ],
    style={
        'display': 'flex',
        'flex-direction': 'column',
        'font-family': '"Open Sans", sans-serif'
    }
)


"""
callback
"""
@app.callback(
    [Output('rev_table', 'data'),
     Output("graph_rev", "figure"),
     Output("graph_mom", "figure"),
     Output("graph_yoy", "figure"),
     Output("rev_search_title", "children"),
     Output('rank_rev_table', 'data'), 
     Output('rank_title','children')
     ],
    [Input('submit', 'n_clicks'),
     State("new-dropdown-component", "value"),
     State("minor-dropdown-component", "value"),
     State("st_input", "value")],
    prevent_initial_call=True
)
def update_table(submit, dropdown1, dropdown2, st_input):
    if (st_input == ' ') or (st_input == '') or (st_input == '輸入...')or (st_input == None):
        try:
            if dropdown1 != exchange_industry_name[0]:
                mask = industry[industry['交易所產業分類'] == dropdown1].st_code.astype(str)
                title = dropdown1 + ' '
            else:
                mask = industry[industry['TEJ產業分類'] == dropdown2].st_code.astype(str)
                title = dropdown2 + ' '

            data = db[db.st_code.isin(mask)]
            
            # 產業個股最新營收狀況
            latest_company = data.drop_duplicates('st_code', keep='last')
            latest_company = latest_company.rename({'st_code':'代號', 'st_name':'名稱', 'rev':'營收(百萬)'}, axis=1)
            latest_company = latest_company[order]
            
            # 產業個股最新營收預估狀況
            predict_company = predict[predict['代號'].isin(mask.astype(int))]
            
            # 產業總營收狀況
            data = data.groupby('rev_period', as_index=False).agg({'rev':'sum'})
            data = fn.get_st_mom_yoy(data)
            data_predict = fn.get_month_rev_predict_for_nxt_year_industry(data)
            
            # 繪圖
            REV = fn.get_revpic(data[data.year > 2018], data_predict, (title + ' 各年度月營收'))
            MOM = fn.get_mompic(data[data.year > 2018], data_predict, (title + ' 各年度月營收'))
            YOY = fn.get_yoypic(data[data.year > 2018], data_predict, (title + ' 各年度月營收'))
            
            # 整理營收資訊表
            table = round(data[data.year > 2018].pivot_table(values='rev', index='year', columns='month').reset_index(), 2)
            data_predict.year = data_predict.year.astype(str) + str(' 預估值')
            table = pd.concat([table, data_predict.tail(12).pivot_table(index='year', columns='month', values='rev').reset_index()],axis=0)
            table = table.rename({'year':'年份'}, axis=1).to_dict('records')
            latest_company['代號'] = latest_company['代號'].astype('int')
            predict_company = predict_company.rename({'yoy％':'預估次月yoy％', 'mom％':'預估次月mom％'}, axis=1).drop(['rev_period', '營收(百萬)'], axis=1)
            
            return table, REV, MOM, YOY,(title + ' 各年度月營收'), pd.merge(latest_company, predict_company, on=['代號','名稱']).to_dict('records'), (title + ' 同產業個股營收狀況')
        
        except KeyError:
            print("跳警示通知：該分類沒有相關個股，請重新選擇，並reset")


    else:
        try:
            if (st_input.isdigit() == True):
                st_group = industry[industry.st_code.astype(str) == st_input]['交易所產業分類'].values[0]
                mask = industry[industry['交易所產業分類'] == st_group].st_code.astype(str)
                data = db[db.st_code == st_input]
            else:
                st_group = industry[industry.st_name.astype(str) == st_input]['交易所產業分類'].values[0]
                mask = industry[industry['交易所產業分類'] == st_group].st_code.astype(str)
                data = db[db.st_name == st_input]
                
            # 產業個股最新營收狀況
            latest_company = db[db.st_code.isin(mask)].drop_duplicates('st_code', keep='last')
            latest_company = latest_company.rename({'st_code':'代號', 'st_name':'名稱', 'rev':'營收(百萬)'}, axis=1)
            latest_company = latest_company[order]

            # 產業個股最新營收預估狀況
            predict_company = predict[predict['代號'].isin(mask.astype(int))]

            # 搜尋個股資訊
            data_predict = fn.get_month_rev_predict_for_nxt_year_industry(data)
                
            # 繪圖
            title = data.st_code.iloc[0] + ' ' + data.st_name.iloc[0]
            REV = fn.get_revpic(data[data.year > '2018'], data_predict, (title + ' 各年度月營收'))
            MOM = fn.get_mompic(data[data.year > '2018'], data_predict, (title + ' 各年度月營收'))
            YOY = fn.get_yoypic(data[data.year > '2018'], data_predict, (title + ' 各年度月營收'))
            
            # 整理營收資訊表
            table = round(data[data.year > '2018'].pivot_table(values='rev', index='year', columns='month').reset_index(), 2)
            data_predict.year = data_predict.year.astype(str) + str(' 預估值')
            table = pd.concat([table, data_predict.tail(12).pivot_table(index='year', columns='month', values='rev').reset_index()],axis=0)
            table = table.rename({'year':'年份'}, axis=1).to_dict('records')
            latest_company['代號'] = latest_company['代號'].astype('int')
            predict_company = predict_company.rename({'yoy％':'預估次月yoy％', 'mom％':'預估次月mom％'}, axis=1).drop(['rev_period', '營收(百萬)'], axis=1)    
            return table, REV, MOM, YOY,(title + ' 各年度月營收'), pd.merge(latest_company, predict_company, on=['代號','名稱']).to_dict('records'), (title + ' 同' + st_group + '產業個股營收狀況')
        
        except IndexError:
            print('跳警示通知：查無該股票營收，請重新輸入，並reset')

