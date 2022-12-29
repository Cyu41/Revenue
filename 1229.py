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

########################### 整理資料 ###########################
# df = pd.read_csv('https://raw.githubusercontent.com/Cyu41/Revenue/main/data_visualize.csv', encoding='utf_8_sig', low_memory=False)
df = pd.read_csv('data_visualize.csv', encoding='utf_8_sig', low_memory=False)
df['Year'] = df.date.str[0:4]
df['month'] = df.date.str[5:7]

# revenue = pd.read_excel('https://raw.githubusercontent.com/Cyu41/Revenue/blob/main/1217_營收.xlsx', sheet_name='RUN1', encoding='utf_8_sig', low_memory=False)
revenue = pd.read_excel('1217_營收.xlsx', sheet_name='RUN1')

stock_info = revenue.iloc[:, 0:3].dropna().rename(
    {'公司簡稱':'company', 'TSE新產業名':'new_name', 'TEJ子產業名':'minor_name'}, axis=1)
stock_info['st_code'] = stock_info.company.str[0:4]
stock_info['st_name'] = stock_info.company.str[5:]
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()
########################### Function ###########################
def get_ratio(data):
    data['ratio'] = round(data.rev/data.rev.sum(), 4)
    return data

def get_avg_ratio(data):
    data = data.sort_values('Year').reset_index(drop=True, inplace=False).head(-1).tail(5)  # 抓到最後一年的前五年
    return round(np.average(data.ratio, weights = weight), 4)

def get_yoy(data):
    data = data.sort_values('Year')
    data['yoy'] = data.rev.diff()/data.rev.shift(1)
    return data

def get_stock_data(st_data):
    st_data['mom'] = st_data.rev.diff()/st_data.rev.shift(1)
    st_yoy = round(st_data.groupby('month').apply(get_yoy), 4)
    return st_yoy.loc[:, ['st_name', 'date', 'rev', 'mom', 'yoy']].tail(1)

weight = [1, 1, 1, 3, 5]

def get_ratio(data):
    data['ratio'] = round(data.rev/data.rev.sum(), 4)
    return data

def get_avg_ratio(data):
    roll_num = len(weight)
    data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
    return round(np.average(data.ratio, weights = weight), 4)

def predict(data):
    data = data.groupby('Year', as_index=False).apply(get_ratio)
    ratio = pd.DataFrame(data.groupby('month', as_index=False).apply(get_avg_ratio)).set_axis(['month', 'wt_avg_ratio'],axis=1)
    predict = pd.merge(data, ratio, on='month', how='outer').sort_values('date').reset_index(drop=True,inplace=False).tail(12)  # 僅向後預測一年
    predict['predict_annul_rev'] = round(predict.rev / predict.ratio)
    predict['predict_month_rev'] = round(round(predict['predict_annul_rev'].mean(), 2) * predict.wt_avg_ratio)
    # # predict['predict_month_rev_v2'] = round(round(np.average(predict.predict_annul_rev.tail(5)/predict.ratio.tail(5), weights = weight), 2) * predict.wt_avg_ratio)
    predict['Year'] = (predict.Year.astype(int) + 1).astype(str)
    predict['rev'] = predict['predict_month_rev']
    predict = pd.concat([data.sort_values('date'), predict], axis=0).sort_values(['Year', 'month'])
    predict['mom'] = predict.rev.diff() / predict.rev.shift(1)
    predict = predict.groupby('month', as_index=False).apply(get_yoy).sort_values(['Year', 'month'])
    return predict.tail(13)

def rank_table(data):
    ranking = data.groupby('st_code', as_index=True).apply(get_stock_data).reset_index(drop=False, inplace=False).reset_index()
    ranking['index'] = ranking['index'] + 1
    ranling = round(ranking, 4)
    ranking = ranking.rename({'index':'排名', 'st_code':'公司代碼', 'st_name':'公司簡稱', 'date':'最新公告月份', 'rev':'營收', 'mom':'MOM%', 'yoy':'YOY%'}, axis=1)
    ranking = ranking.to_dict('records')
    return ranking


def get_mompic(st_data, st_predict, pic_title):
    MOM_pic = []
    for i in st_data.Year.drop_duplicates():
        globals()['trace' + str(i)] = go.Scatter(x=st_data[st_data.Year == i].month, y=st_data[st_data.Year == i].mom, name=i, opacity=0.5)
        MOM_pic.append(globals()['trace' + str(i)])
    for i in st_predict.Year.drop_duplicates():
        globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.Year == i].month, y=st_predict[st_predict.Year == i].mom, name=str(i) + '預估值', #marker_color='black',
                                                         line=dict(dash = "dash"), connectgaps=False)
        MOM_pic.append(globals()['trace_predict' + str(i)])
    layout = go.Layout(title=pic_title+' MOM %', xaxis_title="月份",yaxis_title="MOM %", hovermode='x unified', legend_title_text='年份')
    MOM = go.Figure(data = MOM_pic, layout=layout)
    return MOM

def get_yoypic(st_yoy, st_predict, pic_title):
    YOY_pic = []
    for i in st_yoy.Year.drop_duplicates():
        globals()['trace' + str(i)] = go.Scatter(x=st_yoy[st_yoy.Year == i].month, y=st_yoy[st_yoy.Year == i].yoy, name=i, opacity=0.5)
        YOY_pic.append(globals()['trace' + str(i)])
    for i in st_predict.Year.drop_duplicates():
        globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.Year == i].month, y=st_predict[st_predict.Year == i].yoy, name=str(i) + '預估值',  #marker_color='black',
                                                         line=dict(dash = "dash"), connectgaps=False)
        YOY_pic.append(globals()['trace_predict' + str(i)])
    layout = go.Layout(title=pic_title+' YOY %', xaxis_title="月份",yaxis_title="YOY %", hovermode='x unified', legend_title_text='年份')
    YOY = go.Figure(data = YOY_pic, layout=layout)
    return YOY


def get_revpic(st_data, st_predict, title_name):
    REV_pic = []
    for i in st_data.Year.drop_duplicates():
        globals()['trace' + str(i)] = go.Bar(x=st_data[st_data.Year == i].month, y=st_data[st_data.Year == i].rev, name=i, opacity=0.7)
        REV_pic.append(globals()['trace' + str(i)])
    trace_predict = go.Bar(x=st_predict.month, y=st_predict.predict_month_rev, opacity=1,
                           marker_color='black', name='預估值', marker_pattern_shape="\\",
                           marker=dict(color="white", line_color="black", pattern_fillmode="replace"))
    REV_pic.append(trace_predict)
    layout = go.Layout(barmode = 'group', title=title_name, xaxis_title="月份", yaxis_title="累計營收", hovermode='x unified', legend_title_text='年份')
    REV = go.Figure(data = REV_pic, layout=layout)
    return REV
########################### 整理資料 ###########################

dbc_css = "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server
head = html.Div([html.H1('上市櫃產業年度合併報表')],
                style={'font_size': '600px', 'text_align': 'center'})

new_industry = html.Div(
    [dbc.Label("選擇 TEJ 產業分類"), dcc.Dropdown(
        id="new_industry-dropdown", options=new_industry_name,
        value=new_industry_name[0], optionHeight=50, clearable=False), ],  # style={'width':'80%'},
    className="mb-4",
)

# minor_industry = html.Div(
#     [dbc.Label("選擇 TEJ 子產業分類"), dcc.Dropdown(
#         id="minor_industry-dropdown", options=minor_industry_name,
#         value=minor_industry_name[0], optionHeight=50, clearable=False), ],  # style={'width':'80%'},
#     className="mb-4",
# )

stock = html.Div(
    [
        dbc.Label("輸入股號或公司名稱查詢"),
        dbc.Input(placeholder="輸入...", id='stock_code', type='text', autoComplete=True),
        # dbc.FormText("Type something in the box above"),
    ]
)

button = html.Div(
    [
        dbc.Button(
            "送出查詢", id="submit", className="submit",color="secondary", outline=True, n_clicks=0
        ),
        # html.Span(id="example-output", style={"verticalAlign": "middle"}),
    ]
)

year_slider = html.Div([
    dcc.RangeSlider(2002, 2022, 1, value=[2018, 2022], id='year_slider',tooltip={"placement": "bottom", "always_visible": True}),
    # html.Div(id='output-container-range-slider')
])

controls = dbc.Card(
    [new_industry, stock, year_slider, button],
    body=True,
)

pic = dbc.Card(
    [dcc.Graph(id="graph_rev"),
     dcc.Graph(id="graph_mom"),
     dcc.Graph(id="graph_yoy")],
    body=True,
)

rank_col = ['排名', '公司代碼', '公司簡稱', '最新公告月份', '營收', 'MOM%', 'YOY%']

rank = html.Div([
    html.P("同產業合併月營收排名"),
    html.Div(
        dash_table.DataTable(
            id='rank_table',
            columns=[{"name": i, "id": i, "deletable": True} for i in (rank_col)],
            page_current=0,
            page_size=20,
            # page_action='custom',
            style_cell={
                'font_size': '16px'
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
ranks = dbc.Card(
    [rank],
    body=True,
)

table_col = ['Year'] + ["%.2d" % i for i in range(1, 13)]

table = html.Div([
    html.P("各年度月營收"),
    html.Div(
        dash_table.DataTable(
            id='rev_table',
            columns=[{"name": i, "id": i, "deletable": True} for i in (table_col)],
            page_current=0,
            page_size=10,
            # page_action='custom',
            style_cell={
                'font_size': '16px'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'Year'},
                    'textAlign': 'left'
                }
            ]
        ),
        className="dbc-row-selectable",
    )
])
tables = dbc.Card(
    [table],
    body=True,
)

app.layout = html.Div([
    html.Div([
        head,
    ]),
    html.Div([
        dbc.Col([tables]),
    ]),
    html.Div([
        # dbc.Row([dbc.Col([controls, ranks]), dbc.Col([pic])]),
        dbc.Row([dbc.Col([controls, ranks], width=5), dbc.Col([pic], width=7)]),
    ])
])





@app.callback(
    [Output('rev_table', 'data'),
     Output('rank_table', 'data'),
     Output("graph_rev", "figure"),
     Output("graph_mom", "figure"),
     Output("graph_yoy", "figure")],
    [Input('submit', 'n_clicks'),
     State('year_slider', 'value'),
     State("new_industry-dropdown", "value"),
     State("stock_code", "value")],
    prevent_initial_call=True
)
def update_table(submit, year, dropdown1, stock):
    years = [str(year[0]),str(year[1])]
    if stock is None or stock == '':
        mask = (stock_info.new_name == dropdown1)
        if stock_info[mask].st_code.count() == 0:
            print('Invalid request.')
        else:
            data = pd.merge(stock_info[mask].st_code, df, on='st_code', how='inner')
            data = data[(data.Year >= str(int(years[0]) - 1)) & (data.Year <= years[1])]
            ranking = rank_table(data)

            data = data.groupby(by=['date', 'Year', 'month'], as_index=False).agg({'rev': 'sum'})
            idt_predict = predict(data)
            data['mom'] = data.rev.diff() / data.rev.shift(1)

            yoy = data.groupby(by=['month', 'Year']).agg({'rev': 'sum'}).reset_index()
            yoy = yoy.groupby('month').apply(get_yoy)

            # adjust data periods
            data = data[data.Year != str(int(years[0]) - 1)]
            yoy = yoy[yoy.Year != str(int(years[0]) - 1)]
            TABLE = data.pivot_table(index='Year', columns='month', values='rev').reset_index()
            idt_predict.Year = idt_predict.Year + str(' 預估值')
            TABLE = pd.concat(
                [TABLE, idt_predict.tail(12).pivot_table(index='Year', columns='month', values='rev').reset_index()],
                axis=0)
            TABLE = TABLE.to_dict('records')

            # # # generating figures
            REV = get_revpic(data, idt_predict, dropdown1 + ' ' + ' 各年度月營收')
            MOM = get_mompic(data, idt_predict, dropdown1 + ' ' + ' 各年度月營收')
            YOY = get_yoypic(yoy, idt_predict, dropdown1 + ' ' + ' 各年度月營收')
            return TABLE, ranking, REV, MOM, YOY

    else:
        if (stock.isdigit() == True):
            mask = (stock_info.st_code == stock)
            mask = (stock_info[mask].new_name.iloc[0])
            industry = stock_info[stock_info.new_name == mask]

            data = pd.merge(industry.st_code, df, on='st_code', how='inner')
            data = data[(data.Year >= str(int(years[0]) - 1)) & (data.Year <= years[1])]

            st_name = stock_info[stock_info.st_code == stock].company.values[0]

            st_data = df[df.st_code == stock]
            st_predict = predict(st_data)

            st_data = st_data[(st_data.Year >= str(int(years[0]) - 1)) & (st_data.Year <= years[1])]
            st_data['mom'] = st_data.rev.diff() / st_data.rev.shift(1)
            st_yoy = st_data.groupby('month').apply(get_yoy)

            # adjust data periods
            st_data = st_data[st_data.Year != str(int(years[0]) - 1)]
            st_yoy = st_yoy[st_yoy.Year != str(int(years[0]) - 1)]

            # ranking for the whole industry
            ranking = rank_table(data)

            # data sorting result
            st_TABLE = st_data.pivot_table(index='Year', columns='month', values='rev').reset_index()
            st_predict.Year = st_predict.Year + str(' 預估值')
            st_TABLE = pd.concat(
                [st_TABLE, st_predict.tail(12).pivot_table(index='Year', columns='month', values='rev').reset_index()],
                axis=0)
            st_TABLE = st_TABLE.to_dict('records')

            # # # make a figure
            REV = get_revpic(st_data, st_predict, (st_name + ' 各年度月營收'))
            MOM = get_mompic(st_data, st_predict, (st_name + ' 各年度月營收'))
            YOY = get_yoypic(st_yoy, st_predict, (st_name + ' 各年度月營收'))
            return st_TABLE, ranking, REV, MOM, YOY


        else:
            mask = (stock_info.st_name == stock)
            mask = (stock_info[mask].new_name.iloc[0])
            industry = stock_info[stock_info.new_name == mask]

            data = pd.merge(industry.st_name, df, on='st_name', how='inner')
            data = data[(data.Year >= str(int(years[0]) - 1)) & (data.Year <= years[1])]

            # ranking for the whole industry
            ranking = rank_table(data)

            st_name = stock_info[stock_info.st_name == stock].company.values[0]
            st_data = df[df.st_name == stock]
            st_predict = predict(st_data)

            st_data = st_data[(st_data.Year >= str(int(years[0]) - 1)) & (st_data.Year <= years[1])]
            st_data['mom'] = st_data.rev.diff() / st_data.rev.shift(1)
            st_yoy = st_data.groupby('month').apply(get_yoy)

            # adjust data periods
            st_data = st_data[st_data.Year != str(int(years[0]) - 1)]
            st_yoy = st_yoy[st_yoy.Year != str(int(years[0]) - 1)]

            # data sorting result
            st_TABLE = st_data.pivot_table(index='Year', columns='month', values='rev').reset_index()
            st_predict.Year = st_predict.Year + str(' 預估值')
            st_TABLE = pd.concat(
                [st_TABLE, st_predict.tail(12).pivot_table(index='Year', columns='month', values='rev').reset_index()],
                axis=0)
            st_TABLE = st_TABLE.to_dict('records')

            # # # make a figure
            REV = get_revpic(st_data, st_predict, (st_name + ' 各年度月營收'))
            MOM = get_mompic(st_data, st_predict, (st_name + ' 各年度月營收'))
            YOY = get_yoypic(st_yoy, st_predict, (st_name + ' 各年度月營收'))
            return st_TABLE, ranking, REV, MOM, YOY



if __name__ == '__main__':
    app.run_server(port=8000, debug=True)