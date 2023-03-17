import pandas as pd
import numpy as np


def get_yoy(data):
    data = data.sort_values('Year')
    data['yoy'] = round(data.rev.diff()/data.rev.shift(1), 4)
    return data


def get_st_mom_yoy(data):
    data['Year'] =  data.rev_period.astype(str).str[0:4]
    data['month'] = data.rev_period.astype(str).str[5:7]
    data['mom'] = round(data.rev.diff()/data.rev.shift(1), 4)
    yoy = pd.DataFrame()
    yoy = data.groupby('month').apply(get_yoy).reset_index(drop=True, inplace=False)
    return yoy#[yoy.Year >= '2016']


def get_ratio(data):
    ttl_rev = data.rev.sum()/len(data)*12
    data['ratio'] = round(data.rev/ttl_rev, 4)
    return data


def get_avg_ratio(data):
    if len(data) >= 5:
        weight = [1, 1, 1, 3, 5]
        roll_num = len(weight)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) >= 4:
        weight = [1, 1, 2, 3]
        roll_num = len(weight)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) >= 3:
        weight = [1, 1, 2]
        roll_num = len(weight)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(np.average(data.ratio, weights = weight), 4)
    
    elif len(data) >= 2:
        roll_num = len(data)
        data = data.sort_values('Year').reset_index(drop=True, inplace=False).tail(roll_num + 1).head(roll_num)  # 抓到最後一年的前 n 年，n 隨權重年份個變
        return round(data.ratio.mean(), 4)
        

def get_predict(data):
    if data.shape[0] >= 10:
        a = data.groupby('Year', as_index=False).apply(get_ratio)
        ratio = pd.DataFrame(a.groupby('month', as_index=False).apply(get_avg_ratio)).set_axis(['month', 'wt_avg_ratio'],axis=1)
        predict = pd.merge(a, ratio, on='month', how='outer').sort_values('rev_period').reset_index(drop=True,inplace=False).tail(12)  # 僅向後預測一年
        predict['predict_annul_rev'] = round(predict.rev / predict.ratio)
        predict['predict_month_rev'] = round(predict['predict_annul_rev'].tail(12).mean()* predict.wt_avg_ratio)
        predict['Year'] = (predict.Year.astype(int) + 1).astype(str)
        predict['rev'] = predict['predict_month_rev']
        predict = pd.concat([data.sort_values('rev_period'), predict], axis=0).sort_values(['Year', 'month'])
        predict['mom'] = predict.rev.diff() / predict.rev.shift(1)
        predict = predict.groupby('month', as_index=False).apply(get_yoy).sort_values(['Year', 'month'])
        predict['rev_period'] = '* ' + predict.Year + '/' + predict.month
        predict = predict.drop(['ratio','wt_avg_ratio','predict_annul_rev','predict_month_rev'], axis=1)
        return predict.tail(12)
    else:
        print(data.st_code.head(1).values[0], data.shape[0])