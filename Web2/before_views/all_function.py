import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff  # 圖形工廠
from plotly.subplots import make_subplots  # 繪製子圖
from sklearn.linear_model import LinearRegression
from statsmodels.regression.rolling import RollingOLS, RollingWLS

def latest_return(data):
    data['近一日漲跌％'] = round(data.Close.pct_change(1), 4)
    data['近一週漲跌％'] = round(data.Close.pct_change(5), 4)
    data['近一月漲跌％'] = round(data.Close.pct_change(20), 4)
    return data



# def get_yoy(data):
#     data = data.sort_values('Year')
#     data['yoy'] = round(data.rev.diff()/data.rev.shift(1), 4)
#     return data

# def get_st_mom_yoy(data):
#     data['Year'] =  data.rev_period.astype(str).str[0:4]
#     data['month'] = data.rev_period.astype(str).str[5:7]
#     data['mom'] = round(data.rev.diff()/data.rev.shift(1), 4)
#     yoy = pd.DataFrame()
#     yoy = data.groupby('month').apply(get_yoy).reset_index(drop=True, inplace=False)
#     return yoy[yoy.Year >= '2016']

def get_latest(data):
    latest = data.drop_duplicates(subset='st_code', keep='last')
    # latest = latest.drop('index', axis=1)
    latest = latest.sort_values('declaration_date', ascending=True)
    latest['mom'] = round(latest['mom'], 4)
    latest['yoy'] = round(latest['yoy'], 4)
    latest = latest.loc[:, ['st_code', 'st_name', 'declaration_date', 'rev', 'mom', 'yoy']]
    latest = latest.set_axis(['公司代碼', '公司簡稱', '最新公告日期', '營收', 'MOM%', 'YOY%'], axis=1)
    return latest.to_dict('records')

# def get_mompic(st_data, st_predict, pic_title):
#     MOM_pic = []
#     for i in st_data.Year.drop_duplicates():
#         globals()['trace' + str(i)] = go.Scatter(x=st_data[st_data.Year == i].month, y=st_data[st_data.Year == i].mom, name=i, opacity=0.5)
#         MOM_pic.append(globals()['trace' + str(i)])
#     for i in st_predict.Year.drop_duplicates():
#         globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.Year == i].month, y=st_predict[st_predict.Year == i].mom, name=str(i) + '預估值', #marker_color='black',
#                                                          line=dict(dash = "dash"), connectgaps=False)
#         MOM_pic.append(globals()['trace_predict' + str(i)])
#     layout = go.Layout(title=pic_title+' MOM %', xaxis_title="月份", yaxis_title="MOM %", hovermode='x unified', legend_title_text='年份')
#     MOM = go.Figure(data = MOM_pic, layout=layout)
#     return MOM


# def get_yoypic(st_yoy, st_predict, pic_title):
#     YOY_pic = []
#     for i in st_yoy.Year.drop_duplicates():
#         globals()['trace' + str(i)] = go.Scatter(x=st_yoy[st_yoy.Year == i].month, y=st_yoy[st_yoy.Year == i].yoy, name=i, opacity=0.5)
#         YOY_pic.append(globals()['trace' + str(i)])
#     for i in st_predict.Year.drop_duplicates():
#         globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.Year == i].month, y=st_predict[st_predict.Year == i].yoy, name=str(i) + '預估值',  #marker_color='black',
#                                                          line=dict(dash = "dash"), connectgaps=False)
#         YOY_pic.append(globals()['trace_predict' + str(i)])
#     layout = go.Layout(title=pic_title+' YOY %', xaxis_title="月份", yaxis_title="YOY %", hovermode='x unified', legend_title_text='年份')
#     YOY = go.Figure(data = YOY_pic, layout=layout)
#     return YOY


# def get_revpic(st_data, st_predict, title_name):
#     REV_pic = []
#     for i in st_data.Year.drop_duplicates():
#         globals()['trace' + str(i)] = go.Bar(x=st_data[st_data.Year == i].month, y=st_data[st_data.Year == i].rev, name=i, opacity=0.7)
#         REV_pic.append(globals()['trace' + str(i)])
#     trace_predict = go.Bar(x=st_predict.month, y=st_predict.predict_month_rev, opacity=1,
#                            marker_color='black', name='預估值', marker_pattern_shape="\\",
#                            marker=dict(color="white", line_color="black", pattern_fillmode="replace"))
#     REV_pic.append(trace_predict)
#     layout = go.Layout(barmode = 'group', title=title_name, xaxis_title="月份", yaxis_title="累計營收", hovermode='x unified', legend_title_text='年份')
#     REV = go.Figure(data = REV_pic, layout=layout)
#     return REV


# weight = [1, 1, 1, 3, 5]


# def get_ratio(data):
#     data['ratio'] = round(data.rev/data.rev.sum(), 4)
#     return data


# def get_avg_ratio(data):
#     roll_num = len(weight)
#     data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
#     return round(np.average(data.ratio, weights = weight), 4)


# def predict(data):
#     a = data.groupby('Year', as_index=False).apply(get_ratio)
#     ratio = pd.DataFrame(a.groupby('month', as_index=False).apply(get_avg_ratio)).set_axis(['month', 'wt_avg_ratio'],axis=1)
#     predict = pd.merge(a, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)  # 僅向後預測一年
#     predict['predict_annul_rev'] = round(predict.rev / predict.ratio)
#     predict['predict_month_rev'] = round(round(predict['predict_annul_rev'].mean(), 2) * predict.wt_avg_ratio)
#     predict['Year'] = (predict.Year.astype(int) + 1).astype(str)
#     predict['rev'] = predict['predict_month_rev']
#     predict = pd.concat([data.sort_values('rev_period'), predict], axis=0).sort_values(['Year', 'month'])
#     predict['mom'] = predict.rev.diff() / predict.rev.shift(1)
#     predict = predict.groupby('month', as_index=False).apply(get_yoy).sort_values(['Year', 'month'])
#     return predict.tail(13)



def get_wet_reg(data):
    if data.shape[0] < 5 :
        return []
    data = data.tail(5)
    sample_weight = [1, 1, 2, 3, 5]

    gpm = LinearRegression()
    gpm.fit(np.array(data['營業收入淨額']).reshape(-1, 1), np.array(data['營業毛利']), sample_weight)
    gpm_intercept = round(gpm.intercept_, 2)
    gpm_coef = gpm.coef_[0]

    opm = LinearRegression()
    opm.fit(np.array(data['營業收入淨額']).reshape(-1, 1), np.array(data['營業利益']), sample_weight)
    opm_intercept = round(opm.intercept_, 2)
    opm_coef = opm.coef_[0]
    return [gpm_intercept, round(gpm_coef, 2), opm_intercept, round(opm_coef, 2)]


def forecast_income_statement(data):
    data = data.tail(6)
    data = data.loc[:, ['代號', '名稱', '年/月', '營業收入淨額q', 'est_cost', 'est_gmp', 'est_expense', 'other_expense',
                    'est_opm', 'non_operating_pnl', 'ebit', 'tax_expense', 'controless_pnl','net_income_margin', 
                    '加權平均股數', 'eps_est']]
    data = data.rename({'est_cost':'營業成本', 'est_gmp':'營業毛利', 'est_expense':'營業費用',
                            'other_expense':'其他收益及費損淨額', 'est_opm':'營業利益', 
                            'non_operating_pnl':'營業外收入及支出', 'ebit':'稅前淨利', 'tax_expense':'所得稅費用', 
                            'controless_pnl':'歸屬非控制權益淨利（損）', 'net_income_margin':'稅後淨利', 
                            'eps_est':'每股盈餘'}, axis=1).reset_index(drop=True).transpose()
    return data

def weighted_forecast_estimation(forecast_data, forecast_df):
    t = forecast_data.rolling(5)
    WLS = pd.DataFrame((map(get_wet_reg,t))).set_axis(['gpm_fixed_cost', 'gpm_variable_cost', 
                                                       'opm_fixed_cost', 'opm_variable_cost'], axis=1)
    WLS
    forecast_data = pd.concat([forecast_data.reset_index(drop=True), WLS], axis=1)
    result = pd.merge(forecast_df, forecast_data, how='outer').sort_values('年/月')

    result['other_expense'] = trimmean(result['其他收益及費損淨額'])
    result['non_operating_pnl'] = trimmean(result['營業外收入及支出'])
    result['tax'] = 0.8
    result['controless_pnl'] = trimmean(result['歸屬非控制權益淨利（損）'])

    # estimate forecasting data
    result = pd.concat([result.loc[:, ['代號', '名稱', '年/月', '營業收入淨額q', '營業收入淨額', '營業成本', '營業毛利', 
                                       '營業費用','其他收益及費損淨額', '營業利益', '營業外收入及支出', '稅前淨利', 
                                       '所得稅費用', '歸屬非控制權益淨利（損）', '稅後淨利est','加權平均股數', '每股盈餘']].shift(-1), 
                        result.loc[:, ['gpm_fixed_cost', 'gpm_variable_cost', 'opm_fixed_cost', 'opm_variable_cost',
                                       'other_expense', 'non_operating_pnl', 'tax', 'controless_pnl']]], axis=1)
    result['代號'] = result['代號'].fillna(method='ffill')
    result['名稱'] = result['名稱'].fillna(method='ffill')
    result['加權平均股數'] = result['加權平均股數'].fillna(method='ffill')
    result = result[result['加權平均股數'] > 0]
    result['營業收入淨額q'] = result['營業收入淨額q'].astype(float)
    result['est_cost'] = result['營業收入淨額q'] - (result['營業收入淨額q']*result.gpm_variable_cost + result.gpm_fixed_cost)
    result['est_gmp'] = result['營業收入淨額q']*result.gpm_variable_cost + result.gpm_fixed_cost

    result['est_expense'] = result['est_gmp'] - (result['營業收入淨額q']*result.opm_variable_cost + result.opm_fixed_cost)
    result['est_opm'] = result.est_gmp - result.est_expense

    result['ebit'] = result['est_opm'] + result['other_expense'] + result['non_operating_pnl']
    result['tax_expense'] = result['ebit']*0.2
    result['net_income_margin'] = result['ebit']*0.8 - result['controless_pnl']
    result['eps_est'] = round(result.net_income_margin*1000/ result['加權平均股數'], 2)
    result = result[result['est_cost'].isna() == False]
    result['年/月'].iloc[-1] = result['年/月'].iloc[-1] + ' 預估值'
    return result

def trimmean(data):
    rolling_num = 5
    count = round((data.rolling(rolling_num).sum() - data.rolling(rolling_num).max() 
                   - data.rolling(rolling_num).min())/3, 2)
    return count


def forecast_estimation(forecast_data, forecast_df):
    # gross profit margin
    model = RollingOLS.from_formula("營業毛利 ~ 營業收入淨額", data=forecast_data, window=5)
    gpm_reg = model.fit()
    gpm_reg = round(gpm_reg.params.rename({'Intercept':'gpm_fixed_cost', '營業收入淨額':'gpm_variable_cost'}, axis=1), 2)

    # operating profit margin
    model = RollingOLS.from_formula("營業利益 ~ 營業收入淨額", data=forecast_data, window=5)
    opm_reg = model.fit()
    opm_reg = round(opm_reg.params.rename({'Intercept':'opm_fixed_cost', '營業收入淨額':'opm_variable_cost'}, axis=1), 2)

    result = pd.concat([forecast_data, gpm_reg], axis=1)
    result = pd.concat([result, opm_reg], axis=1)

    result = pd.merge(forecast_df, result, how='outer').sort_values('年/月')
    result['other_expense'] = trimmean(result['其他收益及費損淨額'])
    result['non_operating_pnl'] = trimmean(result['營業外收入及支出'])
    result['tax'] = 0.8
    result['controless_pnl'] = trimmean(result['歸屬非控制權益淨利（損）'])

    # estimate forecasting data
    result = pd.concat([result.loc[:, ['代號', '名稱', '年/月', '營業收入淨額q', '營業收入淨額', '營業成本', '營業毛利', 
                                       '營業費用','其他收益及費損淨額', '營業利益', '營業外收入及支出', '稅前淨利', 
                                       '所得稅費用', '歸屬非控制權益淨利（損）', '稅後淨利est', '加權平均股數','每股盈餘']].shift(-1), 
                        result.loc[:, ['gpm_fixed_cost', 'gpm_variable_cost', 'opm_fixed_cost', 'opm_variable_cost',
                                       'other_expense', 'non_operating_pnl', 'tax', 'controless_pnl']]], axis=1)
    result['代號'] = result['代號'].fillna(method='ffill')
    result['名稱'] = result['名稱'].fillna(method='ffill')
    result['加權平均股數'] = result['加權平均股數'].fillna(method='ffill')
    result = result[result['加權平均股數'] > 0]
    result['營業收入淨額q'] = result['營業收入淨額q'].astype(float)
    result['est_cost'] = result['營業收入淨額q'] - (result['營業收入淨額q']*result.gpm_variable_cost + result.gpm_fixed_cost)
    result['est_gmp'] = result['營業收入淨額q']*result.gpm_variable_cost + result.gpm_fixed_cost

    result['est_expense'] = result['est_gmp'] - (result['營業收入淨額q']*result.opm_variable_cost + result.opm_fixed_cost)
    result['est_opm'] = result.est_gmp - result.est_expense

    result['ebit'] = result['est_opm'] + result['other_expense'] + result['non_operating_pnl']
    result['tax_expense'] = result['ebit']*0.2
    result['net_income_margin'] = result['ebit']*0.8 - result['controless_pnl']
    result['eps_est'] = round(result.net_income_margin*1000/ result['加權平均股數'], 2)
    result = result[result['est_cost'].isna() == False]
    result['年/月'].iloc[-1] = result['年/月'].iloc[-1] + ' 預估值'
    return result

"""
function
"""

def get_ratio(data):
    ttl_rev = data.rev.sum() / len(data) * 12
    data['ratio'] = round(data.rev/ttl_rev, 4)
    return data

def get_yoy(data):
    data.year = data.year.astype(int)
    data = data.sort_values('year')
    if data.rev.head(1).isnull== True:
        data['yoy％'] = 100
    else:
        data['yoy％'] = round(data.rev.diff()/data.rev.shift(1) * 100, 2)
    return data


def get_st_mom_yoy(data):
    data['year'] =  data.rev_period.astype(str).str[0:4]
    data['month'] = data.rev_period.astype(str).str[5:7]
    data['mom％'] = round(data.rev.diff()/data.rev.shift(1) * 100, 2)
    yoy = pd.DataFrame()
    yoy = data.groupby('month').apply(get_yoy).reset_index(drop=True, inplace=False)
    return yoy#[yoy.Year >= '2016']


def get_avg_ratio(data):
    if len(data) >= 5:
        weight = [1, 1, 1, 3, 5]
        roll_num = len(weight)
        data = data.sort_values('year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) == 4:
        weight = [1, 1, 2, 3]
        roll_num = len(weight)
        data = data.sort_values('year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) == 3:
        weight = [1, 1, 2]
        roll_num = len(weight)
        data = data.sort_values('year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) <= 2:
        return round(np.nanmean(data.ratio), 4)

ratio_df = pd.DataFrame(db['month'].unique()).rename({0:'month'}, axis=1)

def get_month_rev_predict_for_nxt_year(data):
#     print(data.st_code.head(1).values[0])
    if data.shape[0] >= 12:
        data = data.groupby('year').apply(get_ratio)
        ratio = data.groupby('month', as_index=False).apply(get_avg_ratio).set_axis(['month', 'wt_avg_ratio'],axis=1)
        data = pd.merge(data, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)
        predict_avg_annual_rev = round((data.rev/data.wt_avg_ratio).mean(), 4)
        data['rev'] = round(data.wt_avg_ratio * predict_avg_annual_rev, 2)
        data.year = data.year.astype(int) + 1
        data.rev_period = '* '+ data.year.astype(str) + '/' + data.month
        data = pd.concat([db[db.st_code == data.st_code.head(1).values[0]].tail(12), 
                          data], axis=0)
        data = data.groupby('month', as_index=False).apply(get_yoy)
        data['mom％'] = round(data.rev.pct_change(1) * 100, 2)
        return data.sort_values('rev_period').head(1)
    else:
        data = data.groupby('year').apply(get_ratio)
        ratio = data.groupby('month', as_index=False).apply(get_avg_ratio).set_axis(['month', 'wt_avg_ratio'],axis=1)
        ratio_len = ratio.month.shape[0]
        ratio = pd.merge(ratio_df, ratio, on='month', how='left').sort_values('month')
        ratio.wt_avg_ratio = ratio.wt_avg_ratio.fillna(round((1 - ratio.wt_avg_ratio.sum())/(12-ratio_len), 4))
        data = pd.merge(data, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)
        data[['st_code', 'st_name', 'year']] = data[['st_code', 'st_name', 'year']].fillna(method='pad')
        data.year = np.where(data.rev_period.isna() == False, data.year.astype(int) + 1, data.year)
        data.rev_period = '* ' + data.year.astype(str) + '/' + data.month
        predict_avg_annual_rev = round(np.nanmean(data.rev/data.wt_avg_ratio), 4)
        data['rev'] = round(data.wt_avg_ratio * predict_avg_annual_rev, 2)
        data = pd.concat([db[db.st_code == data.st_code.head(1).values[0]].tail(12), 
                          data], axis=0)
        data = data.groupby('month', as_index=False).apply(get_yoy)
        data['mom％'] = round(data.rev.pct_change(1) * 100, 2)
        return data.sort_values('rev_period').head(1)
    
def get_month_rev_predict_for_nxt_year_industry(data):
#     print(data.st_code.head(1).values[0])
    if data.shape[0] >= 12:
        original_data = data
        data = data.groupby('year').apply(get_ratio)
        ratio = data.groupby('month', as_index=False).apply(get_avg_ratio).set_axis(['month', 'wt_avg_ratio'],axis=1)
        data = pd.merge(data, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)
        predict_avg_annual_rev = round((data.rev/data.wt_avg_ratio).mean(), 4)
        data['rev'] = round(data.wt_avg_ratio * predict_avg_annual_rev, 2)
        data.year = data.year.astype(int) + 1
        data.rev_period = '* '+ data.year.astype(str) + '/' + data.month
        data = pd.concat([original_data.tail(12), data], axis=0)
        data = data.groupby('month', as_index=False).apply(get_yoy)
        data['mom％'] = round(data.rev.pct_change(1) * 100, 2)
        return data.sort_values('rev_period').head(12)
    else:
        original_data = data
        data = data.groupby('year').apply(get_ratio)
        ratio = data.groupby('month', as_index=False).apply(get_avg_ratio).set_axis(['month', 'wt_avg_ratio'],axis=1)
        ratio_len = ratio.month.shape[0]
        ratio = pd.merge(ratio_df, ratio, on='month', how='left').sort_values('month')
        ratio.wt_avg_ratio = ratio.wt_avg_ratio.fillna(round((1 - ratio.wt_avg_ratio.sum())/(12-ratio_len), 4))
        data = pd.merge(data, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)
        data[['st_code', 'st_name', 'year']] = data[['st_code', 'st_name', 'year']].fillna(method='pad')
        data.year = np.where(data.rev_period.isna() == False, data.year.astype(int) + 1, data.year)
        data.rev_period = '* ' + data.year.astype(str) + '/' + data.month
        predict_avg_annual_rev = round(np.nanmean(data.rev/data.wt_avg_ratio), 4)
        data['rev'] = round(data.wt_avg_ratio * predict_avg_annual_rev, 2)
        data = pd.concat([original_data.tail(12), data], axis=0)
        data = data.groupby('month', as_index=False).apply(get_yoy)
        data['mom％'] = round(data.rev.pct_change(1) * 100, 2)
        return data.sort_values('rev_period').head(12)
    
    
def get_revpic(st_data, st_predict, title_name):
    REV_pic = []
    for i in st_data.year.drop_duplicates():
        globals()['trace' + str(i)] = go.Bar(x=st_data[st_data.year == i].month, y=st_data[st_data.year == i].rev, name=i, opacity=0.7)
        REV_pic.append(globals()['trace' + str(i)])
    trace_predict = go.Bar(x=st_predict.month, y=st_predict.rev, opacity=1,
                           marker_color='black', name='預估值', marker_pattern_shape="\\",
                           marker=dict(color="white", line_color="black", pattern_fillmode="replace"))
    REV_pic.append(trace_predict)
    layout = go.Layout(barmode = 'group', title=title_name, xaxis_title="月份", yaxis_title="累計營收", hovermode='x unified', legend_title_text='年份')
    REV = go.Figure(data = REV_pic, layout=layout)
    return REV

def get_mompic(st_data, st_predict, pic_title):
    MOM_pic = []
    for i in st_data.year.drop_duplicates():
        globals()['trace' + str(i)] = go.Scatter(x=st_data[st_data.year == i].month, y=st_data[st_data.year == i]['mom％'], name=i, opacity=0.5)
        MOM_pic.append(globals()['trace' + str(i)])
    for i in st_predict.year.drop_duplicates():
        globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.year == i].month, y=st_predict[st_predict.year == i]['mom％'], name=str(i) + '預估值', #marker_color='black',
                                                         line=dict(dash = "dash"), connectgaps=False)
        MOM_pic.append(globals()['trace_predict' + str(i)])
    layout = go.Layout(title=pic_title+' MOM％', xaxis_title="月份", yaxis_title="MOM％", hovermode='x unified', legend_title_text='年份')
    MOM = go.Figure(data = MOM_pic, layout=layout)
    return MOM


def get_yoypic(st_yoy, st_predict, pic_title):
    YOY_pic = []
    for i in st_yoy.year.drop_duplicates():
        globals()['trace' + str(i)] = go.Scatter(x=st_yoy[st_yoy.year == i].month, y=st_yoy[st_yoy.year == i]['yoy％'], name=i, opacity=0.5)
        YOY_pic.append(globals()['trace' + str(i)])
    for i in st_predict.year.drop_duplicates():
        globals()['trace_predict' + str(i)] = go.Scatter(x=st_predict[st_predict.year == i].month, y=st_predict[st_predict.year == i]['yoy％'], name=str(i) + '預估值',  #marker_color='black',
                                                         line=dict(dash = "dash"), connectgaps=False)
        YOY_pic.append(globals()['trace_predict' + str(i)])
    layout = go.Layout(title=pic_title+' YOY %', xaxis_title="月份", yaxis_title="YOY％", hovermode='x unified', legend_title_text='年份')
    YOY = go.Figure(data = YOY_pic, layout=layout)
    return YOY