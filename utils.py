from bs4 import BeautifulSoup
import json
import pandas_datareader.data as web
import re
import string
from urllib.request import urlopen

from exchange import exchange_list
def dict_builder(key_list,value_list):
    my_dict = {}
    for k,v in zip(key_list,value_list):
        my_dict[k] = v
    return my_dict

def yahoo_price_(symbol,date,exchange=' '):
    if symbol.find(
        '.') >0 and exchange.startswith('TS'):
        temp_symbol = symbol.replace('.','-')+'.TO'
    elif exchange.startswith('TS'):
        temp_symbol = symbol + '.TO'
    else:
        temp_symbol = symbol
    return float(web.DataReader(temp_symbol,'yahoo',
        date,date)['Close'][0])

def _open(url):
    u = urlopen(url)
    content = u.read()
    content = content.decode('UTF-8')
    data = json.loads(content[3:])
    return data[0]

def _soup_open(url):
    u = urlopen(url)
    content = u.read()
    content = content.decode('UTF-8')
    return BeautifulSoup(content,'html.parser')

def google_data_(symbol):
    ticker_dict = {}
    for exchange in exchange_list:
        '''Need to make sure it is the right ticker!'''
        try:
            link = '''http://finance.google.com/finance/info?client=ig&q='''+ '%s:%s'% (
                exchange,symbol)
            info = _open(link)
            ticker_dict[info['e']] = float(info['l_fix'])
        except:
            print('Did not work: '+symbol)
    return ticker_dict

def google_price(symbol,exchange):
        try:
            link = '''http://finance.google.com/finance/info?client=ig&q='''+ '%s:%s'% (
                exchange,symbol)
            info = _open(link)
            return float(info['l_fix'])
        except:
            print('Did not work: ',symbol)

def google_name(ticker):
        try:
            link2 = '''https://www.google.com/finance?q={}'''.format(ticker)
            soup = _soup_open(link2)
            return (soup.title.get_text().split(':')[0].strip(),
                soup.title.getText().split(':')[1].strip())
        except:
            return 'Error','Error'

def google_exchange(symbol):
    ticker_dict = {}
    for exchange in exchange_list:
        try:
            link = '''http://finance.google.com/finance/info?client=ig&q='''+ '%s:%s'% (
                exchange,symbol)
            info = _open(link)
            ticker_dict[symbol] = info['e']
        except:
            print('Bad Link: ',symbol,exchange)
    return ticker_dict

def google_check(name_list,company_name):
    for name in name_list:
        if name.lower().strip() in company_name.lower().strip():
            return name

def name_clean(company):
    stopwords = ['Inc','Corp','LLC','plc','Corporation','PLC','LP','ADR','The']
    remove = string.punctuation
    pattern = r"[{}]".format(remove)
    company = re.sub(pattern,"",company)
    company =company.split()
    company_result = [word for word in company if word not in stopwords]
    return ' '.join(company_result)
