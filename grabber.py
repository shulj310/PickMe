from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json
import pandas_datareader.data as web
import pandas as pd
import sqlite3
import string
import urllib.request
from urllib.request import urlopen

from exchange import exchange_list
import models
from utils import dict_builder

conn = sqlite3.connect('pickme.db')

class new_post:
    def __init__(self,writer_dict,title_list):
        self.id_dict = writer_dict
        self.title_list = title_list
        self.exchange_final = None
        self.name_list = list(writer_dict.keys())
        self.df = pd.DataFrame()
        self._grab()
        self.df.to_csv('output.csv')
    def _grab(self):
        for self.fullname in self.name_list:
            self.url = self.id_dict[self.fullname][1]
            self._new_post()

    def _new_post(self):
        self.kill = False
        soup = self.request_(self.url)
        for a in soup.find_all('h2'):
            if a.a.get('title').strip() in self.title_list:
                pass
            else:
                self.title = a.a.get('title')
                self.url = a.a.get('href')
                # try:
                sub_soup = self.request_(self.url)
                for b in sub_soup.find_all('p'):
                    if b.get_text().find(self.fullname) ==1:
                        try:
                            name,date,ticker= b.get_text().split('|')
                        except:
                            self.kill = True
                        self.ticker_list = ticker.split('More on:')[1].strip(
                            ).split(' ')
                        self.date = datetime.strptime(date.strip(
                        ),'%B %d, %Y')
                y = sub_soup.find(id='full_content')
                par = []
                for foo in y:
                    if foo.name == 'p':
                        par.append(foo.get_text())
                    if foo.name == 'div':
                        break
                self.par = ' '.join(par)
                if self.kill:
                    break
                self._try_tickers()
                self._price()
                self._to_db()

                # except:
                #     print('Ticker ERROR',self.title,self.url)
    def _try_tickers(self):
        self.max = 0
        self.link = "http://finance.google.com/finance/info?client=ig&q="
        self.count = 0
        for self.ticker in self.ticker_list:
            for self.exchange in exchange_list:
                self._name()
    def _name(self):
        self.link2 = '''https://www.google.com/finance?q={}%3A{}'''.format(
            self.exchange,self.ticker)
        u = urlopen(self.link2)
        content = u.read()
        content = content.decode('UTF-8')
        soup = BeautifulSoup(content,'html.parser')
        self.name = soup.title.get_text().split(':')[0].strip()
        self._count()
    def _count(self):
        self.count = self.title.count(self.name)*5
        self.count = self.count + self.par.count(self.name.lower())
        short_name = self.name.split(' ')[:-1]
        if len(short_name) > 3:
            short_name = short_name[:-2]
            short_name = ' '.join(short_name).strip(',')
        elif len(short_name) == 0:
            short_name = self.name
        else:
            short_name = ' '.join(short_name).strip(',')
        self.count = self.count + self.par.lower().count(short_name.lower())
        '''IF THE STOCK IS NOT CURRENTLY TRADING ON GOOGLE FINANCE, RESET
        COUNT TO ZERO!!!'''
        print(self.ticker,self.exchange)
        try:
            link = "http://finance.google.com/finance/info?client=ig&q="
            url = link+"%s:%s" % (self.exchange,self.ticker)
            u = urlopen(url)
            content = u.read()
            content = content.decode('UTF-8')
            data = json.loads(content[3:])
            info = data[0]
            check = float(info['l_fix'])
            print(self.ticker,self.count,check)
            if self.count > self.max:
                self.max = self.count
                self.symbol = self.ticker
                self.exchange_final = self.exchange
        except:
            print(self.ticker,self.exchange)
    def _price(self):
        d = datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
        if self.date == d:
            self.date = datetime.today
            link = "http://finance.google.com/finance/info?client=ig&q="
            try:
                url = link+"%s:%s" % (self.exchange_final,self.symbol)
                u = urlopen(url)
                content = u.read()
                content = content.decode('UTF-8')
                data = json.loads(content[3:])
                info = data[0]
                self.price = float(info['l_fix'])
                if self.symbol.find(
                    '.') >0 and self.exchange_final.startswith('TS'):
                    self.currency = 'CAD'
                elif self.exchange_final.startswith('TS'):
                    self.currency = 'CAD'
                else:
                    self.currency = 'USD'
            except:
                print('Price ERROR!',self.symbol)
                self.price = None
        else:
            try:
                self.yahoo_price_(exchange=self.exchange_final)
            except:
                print(self.symbol,self.exchange)

    def _to_db(self):
        # if not self.price is None:
        #     models.Post.create(link=self.url,symbol=self.symbol,
        #         exchange=self.exchange_final,title=self.title,entry_px=self.price,
        #             entry=self.par,writer_id=self.id_dict[self.fullname][0],
        #                 timestamp=self.date)
        self.df = self.df.append(pd.DataFrame(
        {'date':[self.date],'link':[self.url],
            'side':[True],'symbol':[self.symbol],'title':[self.title],
                'exchange':[self.exchange_final],'entry_px':[self.price],
                    'entry':[self.par],'currency':[self.currency],
                        'writer_id':[self.id_dict[self.fullname][0]]}))


    def request_(self,url,headers={'User-Agent':'''Mozilla/5.0
    (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)
    Chrome/33.0.1750.117 Safari/537.36''',}):
        request = urllib.request.Request(url,None,headers)
        response = urllib.request.urlopen(request)
        content = response.read()
        content = content.decode('UTF-8')
        return BeautifulSoup(content,'html.parser')

    def yahoo_price_(self,exchange):
        if self.symbol.find(
            '.') >0 and exchange.startswith('TS'):
            temp_symbol = self.symbol.replace('.','-')+'.TO'
            self.currency = 'CAD'
        elif exchange.startswith('TS'):
            temp_symbol = self.symbol + '.TO'
            self.currency = 'CAD'
        else:
            temp_symbol = self.symbol
            self.currency = 'USD'
        self.price = float(web.DataReader(temp_symbol,'yahoo',
            self.date,self.date)['Close'][0])


writer_dict = {}
for writer in models.Writer.select():
    writer_dict[writer.name] = (writer.id,writer.bio)

title_list = []
for post in models.Post.select():
    title_list.append(post.title)

new_post(writer_dict,title_list)
