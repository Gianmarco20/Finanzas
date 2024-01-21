import pandas as pd
import yfinance as yf
from pyhomebroker import HomeBroker
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from pathlib import Path
import openpyxl

today = dt.date.today() - dt.timedelta(days=1)

def download_tickers(start = dt.date(year = 2023, month = 1, day = 1), end = today):
    broker = 265
    user = 'gcaserta'
    dni = '42193912'
    password = 'CasaPadua23'
    hb = HomeBroker(broker_id = broker)
    hb.auth.login(dni = dni, user = user, password = password, raise_exception = True)

    tickers_arg = ['AL30', 'AL30D', 'GD30', 'TV24', 'YPFD', 'PAMP', 'TGSU2', 'TGNO4', 'CEPU', 'VIST', 'TXAR', 'ALUA']
    tickers_arg_dic = {}

    for ticker in tickers_arg:
        data = hb.history.get_daily_history(symbol = ticker, from_date = start, to_date = end)
        data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d')
        data.set_index(data['date'], inplace = True)
        data.sort_index(ascending = True, inplace = True)
        tickers_arg_dic[ticker] = data['close']

    tickers_usa = ['YPF', '^MERV', 'CL=F', 'BZ=F', 'NG=F']
    tickers_usa_dic = {}

    for ticker in tickers_usa:
        data = yf.download(tickers = ticker, start = f'{start.year}-{start.month}-{start.day}', end = f'{end.year}-{end.month}-{end.day + 1}', auto_adjust = True)['Close']
        tickers_usa_dic[ticker] = data.round(2)

    df_tickers_arg = pd.DataFrame(tickers_arg_dic)
    df_tickers_usa = pd.DataFrame(tickers_usa_dic)

    df_tickers = pd.concat([df_tickers_arg, df_tickers_usa], axis = 1)
    df_tickers.rename(columns={'Close': 'YPF'}, inplace = True)
    df_tickers['MEP'] = (df_tickers['AL30'] / df_tickers['AL30D']).round(2)
    df_tickers['CCL'] = (df_tickers['YPFD'] / df_tickers['YPF']).round(2)
    df_tickers.rename(columns = {'^MERV': 'MERVAL', 'CL=F': 'WTI', 'BZ=F': 'BRENT', 'NG=F': 'GAS NATURAL'}, inplace = True)
    df_tickers.dropna(inplace=True)
    return df_tickers

def download_bcra_data():
    data_bcra = ['usd_of', 'tasa_depositos_30_dias']
    df_list = []

    for link in data_bcra:
        url = f'https://api.estadisticasbcra.com/{link}'
        token = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzIwNDcyMTYsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJjYXNlcnRhZ2lhbm1hcmNvMTlAZ21haWwuY29tIn0.8jQsCCJ_bLd7swWL4WTGpjpUQOxZJtEZ9AiuZw1weIPSt60MOhusq8clN6PB0sRepqroRm4hJOe-h51d4JFRmA'
        r = requests.get(url=url, headers={'Authorization': f'BEARER {token}'})
        data = r.json()
        df = pd.DataFrame(data)
        df['d'] = pd.to_datetime(df['d'], format = '%Y-%m-%d')
        df.set_index(df['d'], inplace = True)
        df = df['v']
        df_list.append(df)

    concatenated_df = pd.concat(df_list, axis=1)
    concatenated_df = concatenated_df[concatenated_df.index >= '2023-01-01']
    concatenated_df.columns = ['A3500', 'TASA INTERES']
    return concatenated_df
    
def create_database(tickers, bcra):
    data = pd.concat(objs = [tickers, bcra], axis=1)
    data.dropna(inplace=True)
    path = Path(r'C:\Users\caser\Desktop\EWS\Data/Tormene.xlsx')
    book = openpyxl.load_workbook(filename=path)
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        data.to_excel(writer, sheet_name='DATA FINANCIERA')

create_database(tickers = download_tickers(), bcra = download_bcra_data())