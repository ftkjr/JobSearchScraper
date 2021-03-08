from bs4 import BeautifulSoup as bs
import requests

def fundamental_metric(soup, metric):
    return soup.find(text = metric).find_next(class_='snapshot-td2').text

def get_fundamental_data(df):
    for symbol in df.index:
        try:
            url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
            soup = bs(requests.get(url, headers=headers).content)
            for m in df.columns:
                df.loc[symbol, m ] = fundamental_metric(soup, m)
        except Exception as e:
            print(symbol, 'not found')
    return df


stock_list = [
    'AMZN','GOOG','PG','KO','IBM','DG','XOM','KO','PEP','MT',
    'NL','RTX','LPL'
    ]

metric = ['Price',
'P/B',
'P/E',
'Forward P/E',
'PEG',
'Debt/Eq',
'EPS (ttm)',
'Dividend %',
'ROE',
'ROI',
'EPS Q/Q',
'Insider Own'
]
