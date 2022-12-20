import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
from dash import Dash, dcc, html, dash_table, Input, Output, callback, State, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

########################### 整理資料 ###########################
df = pd.read_csv('https://github.com/Cyu41/Revenue/blob/main/data_visualize.csv', low_memory=False)
df['Year'] = df.date.str[0:4]
df['month'] = df.date.str[5:7]

revenue = pd.read_excel('/Users/yuchun/Downloads/1217_營收.xlsx', sheet_name='RUN1')
# predict = pd.read_excel('/Users/yuchun/Downloads/1217_營收.xlsx', sheet_name='RUN2')

stock_info = revenue.iloc[:, 0:3].dropna().rename(
    {'公司簡稱':'company', 'TSE新產業名':'new_name', 'TEJ子產業名':'minor_name'}, axis=1)
stock_info['st_code'] = stock_info.company.str[0:4]
stock_info['st_name'] = stock_info.company.str[5:]
new_industry_name = revenue['TSE新產業名.1'].dropna()
minor_industry_name = revenue['TEJ子產業名.1'].dropna()
########################### Function ###########################
def get_yoy(data):
    data = data.sort_values('Year')
    data['yoy'] = data.rev.diff()/data.rev.shift(1)
    return data


def get_3pic(data, yoy, pic_title):
    REV = px.bar(x=data.month, y=data.rev, color=data.Year, barmode='group')
    REV = REV.update_layout(title=pic_title, xaxis_title="月份", yaxis_title="累計營收", hovermode='x unified', legend_title_text='年份')
    MOM = px.line(x = data.month, y=data.mom, color=data.Year)
    MOM = MOM.update_layout(title=pic_title+' MOM %', xaxis_title="月份",yaxis_title="MOM %", hovermode='x unified', legend_title_text='年份')
    YOY = px.line(x = yoy.month, y=yoy.yoy, color=yoy.Year)
    YOY = YOY.update_layout(title=pic_title+' YOY %', xaxis_title="月份",yaxis_title="YOY %", hovermode='x unified', legend_title_text='年份')
    return REV.show(), MOM.show(), YOY.show()

# 三個圖
def get_revpic(data, yoy, pic_title):
    REV = px.bar(x=data.month, y=data.rev, color=data.Year, barmode='group')
    REV = REV.update_layout(title=pic_title, xaxis_title="月份", yaxis_title="累計營收", hovermode='x unified', legend_title_text='年份')
    return REV

def get_mompic(data, yoy, pic_title):
    MOM = px.line(x = data.month, y=data.mom, color=data.Year)
    MOM = MOM.update_layout(title=pic_title+' MOM %', xaxis_title="月份",yaxis_title="MOM %", hovermode='x unified', legend_title_text='年份')
    return MOM

def get_yoypic(data, yoy, pic_title):
    YOY = px.line(x = yoy.month, y=yoy.yoy, color=yoy.Year)
    YOY = YOY.update_layout(title=pic_title+' YOY %', xaxis_title="月份",yaxis_title="YOY %", hovermode='x unified', legend_title_text='年份')
    return YOY
########################### 整理資料 ###########################

dbc_css = "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

head = html.Div([html.H1('上市櫃產業年度合併報表')],
                style={'font_size': '600px', 'text_align': 'center'})

new_industry = html.Div(
    [dbc.Label("選擇 TEJ 產業分類"), dcc.Dropdown(
        id="new_industry-dropdown", options=new_industry_name,
        value=new_industry_name[0], optionHeight=50, clearable=False), ],  # style={'width':'80%'},
    className="mb-4",
)

minor_industry = html.Div(
    [dbc.Label("選擇 TEJ 子產業分類"), dcc.Dropdown(
        id="minor_industry-dropdown", options=minor_industry_name,
        value=minor_industry_name[0], optionHeight=50, clearable=False), ],  # style={'width':'80%'},
    className="mb-4",
)

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
    dcc.RangeSlider(2002, 2022, 1, value=[2018, 2021], id='year_slider'),
    # html.Div(id='output-container-range-slider')
])

controls = dbc.Card(
    [new_industry, minor_industry, stock, year_slider, button],
    body=True,
)

pic = dbc.Card(
    [dcc.Graph(id="graph_rev"),
     dcc.Graph(id="graph_mom"),
     dcc.Graph(id="graph_yoy")],
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
            page_size=5,
            page_action='custom',
            style_cell={
                'font_size': '16px'
            },
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
        dbc.Col([tables]),
    ]),
    html.Div([
        dbc.Row([dbc.Col([controls], width=3), dbc.Col([pic], width=9)]),
    ])
])


@app.callback(
    Output('minor_industry-dropdown', 'options'),
    Input("new_industry-dropdown", "value"),
    prevent_initial_call=True
)
def update_minor_option(industry):
    if industry != new_industry_name[0]:
        minor_option = minor_industry_name[0]
        minor_option.append(minor_industry_name[minor_industry_name.str[0:3] == industry[0:3]])
    else:
        minor_option = minor_industry_name
    return minor_option




@app.callback(
    [Output('rev_table', 'data'),
     Output("graph_rev", "figure"),
     Output("graph_mom", "figure"),
     Output("graph_yoy", "figure")],
    [Input('submit', 'n_clicks'),
     State('year_slider', 'value'),
     State("new_industry-dropdown", "value"),
     State("minor_industry-dropdown", "value"),
     State("stock_code", "value")],
    prevent_initial_call=True
)
def update_table(submit, year, dropdown1, dropdown2, stock):
    years = [str(year[0]),str(year[1])]
    if stock is None or stock == '':
        if (dropdown1 != new_industry_name[0]) & (dropdown2 == minor_industry_name[0]):
            mask = (stock_info.new_name == dropdown1)
            if stock_info[mask].st_code.count() == 0:
                print('Invalid request.')
            else:
                data = pd.merge(stock_info[mask].st_code, df, on='st_code', how='inner')
                data = data[(data.Year >= str(int(years[0]) - 1)) & (data.Year <= years[1])]
                data = data.groupby(by=['Year', 'month']).agg({'rev': 'sum'})
                data['mom'] = data.rev.diff() / data.rev.shift(1)
                data = data.reset_index()

                TABLE = data.pivot_table(index='Year', columns='month', values='rev').reset_index().to_dict('records')

                yoy = data.groupby(by=['month', 'Year']).agg({'rev': 'sum'}).reset_index()
                yoy = yoy.groupby('month').apply(get_yoy)

                # 調整資料年份
                data = data[data.Year != str(int(years[0]) - 1)]
                yoy = yoy[yoy.Year != str(int(years[0]) - 1)]
                # # 繪圖專區
                REV = get_revpic(data, yoy, dropdown1 + ' 各年度月營收')
                MOM = get_mompic(data, yoy, dropdown1 + ' 各年度月營收')
                YOY = get_yoypic(data, yoy, dropdown1 + ' 各年度月營收')
                return TABLE, REV, MOM, YOY

        elif (dropdown1 != new_industry_name[0]) & (dropdown2 != minor_industry_name[0]):
            mask = (stock_info.new_name == dropdown1) & (stock_info.minor_name == dropdown2)
            if stock_info[mask].st_code.count() == 0:
                print('Invalid request.')
            else:
                data = pd.merge(stock_info[mask].st_code, df, on='st_code', how='inner')
                data = data[(data.Year >= str(int(years[0]) - 1)) & (data.Year <= years[1])]
                data = data.groupby(by=['Year', 'month']).agg({'rev': 'sum'})
                data['mom'] = data.rev.diff() / data.rev.shift(1)
                data = data.reset_index()

                TABLE = data.pivot_table(index='Year', columns='month', values='rev').reset_index().to_dict('records')

                yoy = data.groupby(by=['month', 'Year']).agg({'rev': 'sum'}).reset_index()
                yoy = yoy.groupby('month').apply(get_yoy)

                # 調整資料年份
                data = data[data.Year != str(int(years[0]) - 1)]
                yoy = yoy[yoy.Year != str(int(years[0]) - 1)]
                # # 繪圖專區
                REV = get_revpic(data, yoy, dropdown1 + dropdown2 + ' 各年度月營收')
                MOM = get_mompic(data, yoy, dropdown1 + dropdown2 + ' 各年度月營收')
                YOY = get_yoypic(data, yoy, dropdown1 + dropdown2 + ' 各年度月營收')
                return TABLE, REV, MOM, YOY

        elif (dropdown1 == new_industry_name[0]) & (dropdown2 != minor_industry_name[0]):
            mask = (stock_info.minor_name == dropdown2)
            if stock_info[mask].st_code.count() == 0:
                print('Invalid request.')
            else:
                data = pd.merge(stock_info[mask].st_code, df, on='st_code', how='inner')
                data = data[(data.Year >= str(int(years[0]) - 1)) & (data.Year <= years[1])]
                data = data.groupby(by=['Year', 'month']).agg({'rev': 'sum'})
                data['mom'] = data.rev.diff() / data.rev.shift(1)
                data = data.reset_index()

                TABLE = data.pivot_table(index='Year', columns='month', values='rev').reset_index().to_dict('records')

                yoy = data.groupby(by=['month', 'Year']).agg({'rev': 'sum'}).reset_index()
                yoy = yoy.groupby('month').apply(get_yoy)

                # 調整資料年份
                data = data[data.Year != str(int(years[0]) - 1)]
                yoy = yoy[yoy.Year != str(int(years[0]) - 1)]
                # # 繪圖專區
                REV = get_revpic(data, yoy, dropdown1 + dropdown2 + ' 各年度月營收')
                MOM = get_mompic(data, yoy, dropdown1 + dropdown2 + ' 各年度月營收')
                YOY = get_yoypic(data, yoy, dropdown1 + dropdown2 + ' 各年度月營收')
                return TABLE, REV, MOM, YOY

    else:
        if (stock.isdigit() == True):
            st_name = stock_info[stock_info.st_code == stock].company.values[0]

            st_data = df[df.st_code == stock]
            st_data = st_data[(st_data.Year >= str(int(years[0]) - 1)) & (st_data.Year <= years[1])]
            st_data['mom'] = st_data.rev.diff() / st_data.rev.shift(1)

            st_yoy = st_data.groupby('month').apply(get_yoy)

            # adjust data periods
            st_data = st_data[st_data.Year != str(int(years[0]) - 1)]
            st_yoy = st_yoy[st_yoy.Year != str(int(years[0]) - 1)]
            st_TABLE = st_data.pivot_table(index='Year', columns='month', values='rev').reset_index().to_dict('records')

            # # generating figures
            REV = get_revpic(st_data, st_yoy, (st_name + ' 各年度月營收'))
            MOM = get_mompic(st_data, st_yoy, (st_name + ' 各年度月營收'))
            YOY = get_yoypic(st_data, st_yoy, (st_name + ' 各年度月營收'))
            return st_TABLE, REV, MOM, YOY

        else:
            st_name = stock_info[stock_info.st_name == stock].company.values[0]

            st_data = df[df.st_name == stock]
            st_data = st_data[(st_data.Year >= str(int(years[0]) - 1)) & (st_data.Year <= years[1])]
            st_data['mom'] = st_data.rev.diff() / st_data.rev.shift(1)

            st_yoy = st_data.groupby('month').apply(get_yoy)

            # adjust data periods
            st_data = st_data[st_data.Year != str(int(years[0]) - 1)]
            st_yoy = st_yoy[st_yoy.Year != str(int(years[0]) - 1)]
            st_TABLE = st_data.pivot_table(index='Year', columns='month', values='rev').reset_index().to_dict('records')

            # # generating figures
            REV = get_revpic(st_data, st_yoy, (st_name + ' 各年度月營收'))
            MOM = get_mompic(st_data, st_yoy, (st_name + ' 各年度月營收'))
            YOY = get_yoypic(st_data, st_yoy, (st_name + ' 各年度月營收'))
            return st_TABLE, REV, MOM, YOY





if __name__ == '__main__':
    app.run_server(port=8051, debug=True)
