import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖

def get_yoy(data):
    data = data.sort_values('Year')
    data['yoy'] = data.rev.diff()/data.rev.shift(1)
    return data

def get_st_mom_yoy(data):
    data['Year'] =  data.rev_period.astype(str).str[0:4]
    data['month'] = data.rev_period.astype(str).str[5:7]
    data['mom'] = data.rev.diff()/data.rev.shift(1)
    yoy = pd.DataFrame()
    yoy = data.groupby('month').apply(get_yoy).reset_index(drop=True, inplace=False)
    return yoy

def get_latest(data):
    latest = data.drop_duplicates(subset='st_code', keep='last')
    # latest = latest.drop('index', axis=1)
    latest = latest.sort_values('declaration_date', ascending=True)
    latest = latest.loc[:, ['st_code', 'st_name', 'declaration_date', 'rev', 'mom', 'yoy']]
    return latest.to_dict('records')

def get_mompic(st_data, st_predict, pic_title):
    MOM_pic = []
    for i in st_data.Year.drop_duplicates():
        globals()['trace' + str(i)] = go.Scatter(x=st_data[st_data.Year == i].month, y=st_data[st_data.Year == i].mom, name=i, opacity=0.5)
        MOM_pic.append(globals()['trace' + str(i)])
    for i in st_predict.Year.drop_duplicates():
        globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.Year == i].month, y=st_predict[st_predict.Year == i].mom, name=str(i) + '預估值', #marker_color='black',
                                                         line=dict(dash = "dash"), connectgaps=False)
        MOM_pic.append(globals()['trace_predict' + str(i)])
    layout = go.Layout(title=pic_title+' MOM %', xaxis_title="月份", yaxis_title="MOM %", hovermode='x unified', legend_title_text='年份')
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
    layout = go.Layout(title=pic_title+' YOY %', xaxis_title="月份", yaxis_title="YOY %", hovermode='x unified', legend_title_text='年份')
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

weight = [1, 1, 1, 3, 5]

def get_ratio(data):
    data['ratio'] = round(data.rev/data.rev.sum(), 4)
    return data

def get_avg_ratio(data):
    roll_num = len(weight)
    data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
    return round(np.average(data.ratio, weights = weight), 4)

def predict(data):
    a = data.groupby('Year', as_index=False).apply(get_ratio)
    ratio = pd.DataFrame(a.groupby('month', as_index=False).apply(get_avg_ratio)).set_axis(['month', 'wt_avg_ratio'],axis=1)
    predict = pd.merge(a, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)  # 僅向後預測一年
    predict['predict_annul_rev'] = round(predict.rev / predict.ratio)
    predict['predict_month_rev'] = round(round(predict['predict_annul_rev'].mean(), 2) * predict.wt_avg_ratio)
    predict['Year'] = (predict.Year.astype(int) + 1).astype(str)
    predict['rev'] = predict['predict_month_rev']
    predict = pd.concat([data.sort_values('rev_period'), predict], axis=0).sort_values(['Year', 'month'])
    predict['mom'] = predict.rev.diff() / predict.rev.shift(1)
    predict = predict.groupby('month', as_index=False).apply(get_yoy).sort_values(['Year', 'month'])
    return predict.tail(13)
