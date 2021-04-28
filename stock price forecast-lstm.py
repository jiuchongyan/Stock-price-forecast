__author__ = 'samsung'
# ʹ��LSTMԤ�⻦��ָ��
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from pandas import DataFrame
from pandas import concat
from itertools import chain
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt


# ת��Ϊ�������ڼලѧϰ������
def get_train_set(data_set, timesteps_in, timesteps_out=1):
    train_data_set = np.array(data_set)
    reframed_train_data_set = np.array(series_to_supervised(train_data_set, timesteps_in, timesteps_out).values)
    print(reframed_train_data_set)
    print(reframed_train_data_set.shape)
    train_x, train_y = reframed_train_data_set[:, :-timesteps_out], reframed_train_data_set[:, -timesteps_out:]
    # �����ݼ��ع�Ϊ����LSTMҪ������ݸ�ʽ,�� [��������ʱ�䲽������]
    train_x = train_x.reshape((train_x.shape[0], timesteps_in, 1))
    return train_x, train_y

"""
��ʱ����������ת��Ϊ�����ڼලѧϰ������
�������롢������еĳ���
data: �۲�����
n_in: �۲�����input(X)�Ĳ�������Χ[1, len(data)], Ĭ��Ϊ1
n_out: �۲�����output(y)�Ĳ����� ��ΧΪ[0, len(data)-1], Ĭ��Ϊ1
dropnan: �Ƿ�ɾ��NaN��
����ֵ�������ڼලѧϰ�� DataFrame
"""
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # Ԥ������ (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # ƴ�ӵ�һ��
    agg = concat(cols, axis=1)
    agg.columns = names
    # ȥ��NaN��
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# ʹ��LSTM����Ԥ��
def lstm_model(source_data_set, train_x, label_y, input_epochs, input_batch_size, timesteps_out):
    model = Sequential()

    # ��һ��, ���ز���Ԫ�ڵ����Ϊ128, ������������
    model.add(LSTM(128, return_sequences=True, activation='tanh', input_shape=(train_x.shape[1], train_x.shape[2])))
    # �ڶ��㣬���ز���Ԫ�ڵ����Ϊ128, ֻ�����������һ�����
    model.add(LSTM(128, return_sequences=False))
    model.add(Dropout(0.5))
    # ������ ��Ϊ�ǻع���������ʹ��linear
    model.add(Dense(timesteps_out, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer='adam')

    # LSTMѵ�� input_epochs����, verbose = 2 Ϊÿ��epoch���һ�м�¼, =1Ϊ�����������¼, =0 ���ڱ�׼����������־��Ϣ
    res = model.fit(train_x, label_y, epochs=input_epochs, batch_size=input_batch_size, verbose=2, shuffle=False)

    # ģ��Ԥ��
    train_predict = model.predict(train_x)
    #test_data_list = list(chain(*test_data))
    train_predict_list = list(chain(*train_predict))

    plt.plot(res.history['loss'], label='train')
    plt.show()
    print(model.summary())
    plot_img(source_data_set, train_predict)

# ����ԭʼ���ݣ�ѵ���������֤�����Ԥ����
def plot_img(source_data_set, train_predict):
    plt.figure(figsize=(24, 8))
    # ԭʼ������ɫ
    plt.plot(source_data_set[:, -1], c='b')
    # ѵ��������ɫ
    plt.plot([x for x in train_predict], c='g')
    plt.legend()
    plt.show()

# ���ù۲�����input(X)�Ĳ�����ʱ�䲽����epochs��batch_size
timesteps_in = 3
timesteps_out = 3
epochs = 500
batch_size = 100
data = pd.read_csv('./shanghai_index_1990_12_19_to_2020_03_12.csv')
data_set = data[['Price']].values.astype('float64')
# ת��Ϊ�������ڼලѧϰ������
train_x, label_y = get_train_set(data_set, timesteps_in=timesteps_in, timesteps_out=timesteps_out)

# ʹ��LSTM����ѵ����Ԥ��
lstm_model(data_set, train_x, label_y, epochs, batch_size, timesteps_out=timesteps_out)

