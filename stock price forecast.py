__author__ = 'samsung'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm
import warnings
from itertools import product
from datetime import datetime, timedelta
import calendar

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif']=['SimHei'] #����������ʾ���ı�ǩ
# ���ݼ���
df = pd.read_csv('./shanghai_index_1990_12_19_to_2020_03_12.csv')
df = df[['Timestamp', 'Price']]

# ��ʱ����Ϊdf������
df.Timestamp = pd.to_datetime(df.Timestamp)
df.index = df.Timestamp
# ����̽��
print(df.head())
# �����£����ȣ�����ͳ��
df_month = df.resample('M').mean()
df_Q = df.resample('Q-DEC').mean()
df_year = df.resample('A-DEC').mean()
print(df_month)

# ���ò�����Χ
ps = range(0, 5)
qs = range(0, 5)
ds = range(1, 2)
parameters = product(ps, ds, qs)
parameters_list = list(parameters)
# Ѱ������ARMAģ�Ͳ�������best_aic��С
results = []
best_aic = float("inf") # ������
for param in parameters_list:
    try:
        #model = ARIMA(df_month.Price,order=(param[0], param[1], param[2])).fit()
        # SARIMAX ���������������ص�ARIMAģ��
        model = sm.tsa.statespace.SARIMAX(df_month.Price,
                                order=(param[0], param[1], param[2]),
                                #seasonal_order=(4, 1, 2, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False).fit()

    except ValueError:
        print('��������:', param)
        continue
    aic = model.aic
    if aic < best_aic:
        best_model = model
        best_aic = aic
        best_param = param
    results.append([param, model.aic])
# �������ģ��
print('����ģ��: ', best_model.summary())

# ����future_month����ҪԤ���ʱ��date_list
df_month2 = df_month[['Price']]
future_month = 3
last_month = pd.to_datetime(df_month2.index[len(df_month2)-1])
date_list = []
for i in range(future_month):
    # �����¸����ж�����
    year = last_month.year
    month = last_month.month
    if month == 12:
        month = 1
        year = year+1
    else:
        month = month + 1
    next_month_days = calendar.monthrange(year, month)[1]
    #print(next_month_days)
    last_month = last_month + timedelta(days=next_month_days)
    date_list.append(last_month)
print('date_list=', date_list)

# ���δ��ҪԤ���3����
future = pd.DataFrame(index=date_list, columns= df_month.columns)
df_month2 = pd.concat([df_month2, future])

# get_prediction�õ��������䣬ʹ��predicted_mean
df_month2['forecast'] = best_model.get_prediction(start=0, end=len(df_month2)).predicted_mean

# ����ָ��Ԥ������ʾ
plt.figure(figsize=(30,7))
df_month2.Price.plot(label='ʵ��ָ��')
df_month2.forecast.plot(color='r', ls='--', label='Ԥ��ָ��')
plt.legend()
plt.title('����ָ�����£�')
plt.xlabel('ʱ��')
plt.ylabel('ָ��')
plt.show()

