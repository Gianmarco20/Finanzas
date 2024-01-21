import pandas as pd
import datetime as dt
from pyhomebroker import HomeBroker
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import seaborn as sns

def get_tickers():
    panel_lider = pd.read_html('https://es.wikipedia.org/wiki/S%26P_Merval')[1]['Símbolo'].to_list()
    panel_general = pd.read_html('https://es.wikipedia.org/wiki/S%26P_Merval')[2]['Símbolo'].to_list()
    bonos = ['AL30', 'AL30D', 'GD30', 'TV24']
    merval = panel_lider + panel_general + bonos
    
    return merval

def financial_data(user, dni, password, broker, tickers):
    data_dic = {}
    hb = HomeBroker(broker_id = broker)
    hb.auth.login(user = user, dni = dni, password = password, raise_exception = True)
    
    for ticker in tickers:
        data = hb.history.get_daily_history(symbol = ticker, from_date = dt.date(year = 2020, month = 1, day = 1), to_date = dt.date.today())
        data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d')
        data.set_index(data['date'], inplace = True)
        data = data['close']
        data_dic[ticker] = data
    
    financial_df = pd.DataFrame(data = data_dic)
    
    ypf = yf.download(tickers = 'YPF', start = '2020-01-01', end = f'{dt.date.today().year}-{dt.date.today().month}-{(dt.date.today() + dt.timedelta(days = 1)).day}', auto_adjust = True)['Close']

    def bcra_data():
        bcra_data = []
        endpoints = ['usd_of', 'base']
        for endpoint in endpoints:
            url = f'https://api.estadisticasbcra.com/{endpoint}'
            token = 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzI1NDA1NjcsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJjYXNlcnRhZ2lhbm1hcmNvMTlAZ21haWwuY29tIn0.m9yeqLfyfT42VFDswYmnTT2bxCQXadNRIyIWLeLJSNMsND4D9g6o7i77D4MTUWaH8D3P4LOClOJqJQcWizWOwA'
            r = requests.get(url = url, headers = {'Authorization': f'BEARER {token}'})
            data = r.json()
            df = pd.DataFrame(data = data)
            df['d'] = pd.to_datetime(arg = df['d'], format = '%Y-%m-%d')
            df.set_index(keys = 'd', inplace = True)
            df = df['v']
            bcra_data.append(df)

        data = pd.DataFrame(bcra_data).T
        data.columns = ['A3500', 'BASE MONETARIA']
        data = data[data.index >= '2020']

        return data
    
    financial_df = pd.concat(objs = [financial_df, ypf, bcra_data()], axis = 1)
    financial_df.rename(columns = {'Close': 'YPF'}, inplace = True)
    financial_df['MEP'] = round(number = (financial_df['AL30'] / financial_df['AL30D']), ndigits = 2)
    financial_df['CCL'] = round(number = (financial_df['YPFD'] / financial_df['YPF']), ndigits = 2)
    financial_df.drop(columns = ['AL30D', 'YPF'], inplace = True)

    return financial_df

def get_graphics(data):
    data = data.pct_change() + 1
    data = (data.cumprod() - 1) * 100
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize = (12,7))
    plt.plot(data.index, data['TV24'], label = 'TV24')
    plt.plot(data.index, data['A3500'], label = 'A3500')
    plt.plot(data.index, data['CCL'], label = 'CCL')
    plt.plot(data.index, data['MEP'], label = 'MEP')
    plt.legend()
    return plt.show()

get_graphics(data = financial_data(user = 'Gcaserta', dni = '42193912', password = 'CasaPadua23', broker = 265, tickers = get_tickers()))