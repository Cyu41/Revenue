import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
import numpy as np
import schedule
import psycopg2
import psycopg2.extras as extras
from sqlalchemy import create_engine

cluster = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/cluster_industry.csv')
industry = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/industry.csv')
daily_trading = pd.read_csv('/Users/yuchun/Revenue/ML_Cluster/daily_trading.csv', low_memory=False)
group = pd.merge(industry, cluster.loc[:, ['歆凱分組', '代號']], on='代號', how='left').drop('Unnamed: 0', axis=1)

def latest_return(data):
    data['近一日漲跌％'] = round(data.Close.pct_change(1), 4)
    data['近一週漲跌％'] = round(data.Close.pct_change(5), 4)
    data['近一月漲跌％'] = round(data.Close.pct_change(20), 4)
    return data

def get_cluster_group_data(st_input):
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
    df = df.groupby('st_code', as_index=False).apply(latest_return)

    latest = df.loc[:, ['st_code', 'st_name', '近一日漲跌％','近一週漲跌％','近一月漲跌％']].drop_duplicates('st_code', keep='last')
    latest = latest.rename({'st_code':'代號', 'st_name':'名稱'}, axis=1)
    group_return = df.groupby('date', as_index=False).agg({'近一日漲跌％':'mean', '近一週漲跌％':'mean', '近一月漲跌％':'mean'})
    group_return_latest = group_return.tail(1)

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
    return fig, latest.to_dict('records'), group_return_latest.to_dict('records')
