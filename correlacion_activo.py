import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import requests
import datetime as dt

ticker = input('Empresa objetivo: ').upper()
year = input('Desde año: ')

def get_commodities():
    url = 'https://es-us.finanzas.yahoo.com/mercados/materias-primas/'

    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url = url, headers = header)
    commodities = pd.read_html(r.text)[0]['Símbolo'].to_list()
    return commodities

def get_tickers(empresa = ticker, commodities = get_commodities()):
    url = 'https://www.slickcharts.com/sp500'

    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers = header)
    tickers = pd.read_html(r.text)[0]['Symbol'].tolist()
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    all_tickers = tickers + commodities + [empresa]
    return all_tickers

def get_valuations(desde = year, tickers = get_tickers()):
    today = dt.date.today()
    data = yf.download(tickers = tickers, start = f'{desde}-01-01', end = f'{today.year}-{today.month}-{today.day}', auto_adjust = True)['Close'].pct_change()
    return data

def get_correlations(data = get_valuations()):
    correlation = data.corr().round(2)
    col_obj = correlation[f'{ticker}']
    col_obj = col_obj.sort_values(ascending = False)
    col_obj = col_obj.iloc[1:11]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize = (12, 10))
    bar_plot = sns.barplot(x = col_obj.index, y = col_obj.values)
    plt.title(f'Top 10 empresas correlacionadas con {ticker} desde {year} hasta hoy')
    plt.ylabel('Correlación')
    plt.xlabel('Compañías')
    for index, value in enumerate(col_obj):
        bar_plot.text(index, value, str(value), ha='center', va='bottom')
    return plt.show()

get_correlations()