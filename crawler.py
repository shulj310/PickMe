from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import json
import string
import re
import requests
import sys
import urllib.request
from urllib.request import urlopen

from company import company_dictionary,create_company
from exchange import exchange_list
import models
from price import price
from utils import (dict_builder,yahoo_price_,google_price,google_name,
                    google_exchange,google_check,name_clean)

class webCrawl:

    def __init__(self,writer_list):
        self.writer_list = writer_list
        self.writer_dict_init()
        self.comp_dict = company_dictionary()
        self.link_list = self.get_link()
        while True:
            self.zachs()

    def yaFin(self):
        url = 'https://finance.yahoo.com/'
        req = requests.get('http://finance.yahoo.com/')
        soup = BeautifulSoup(req.content,'html5lib')
        for ul in soup.findAll('ul'):
            for li in ul.findAll('li',{'class':'js-stream-content Pos(r)'}):
                link = self.href_(li)
            try:
                url_2 = url+link
                soup2 = self.request_(url=url_2)
                print(soup2.title.get_text())
                for span in soup2.findAll('span',{'class':'provider-link'}):
                    print(span.get_text())
                '''Based on provider, follow the appropriate protocol!'''
                for link in soup2.find_all('a',{'class':'read-more-button'}):
                    link = self.href_(link)
                    soup3 = self.request_(url=link)
                    print(soup3.title.getText())
                    '''This is where the protocol will go based on the
                    provider to direct the appropriate gathering!'''
            except:
                print('fail')

    def zachs(self):
        self.source = 'Zachs'
        self.url = 'https://www.zacks.com'
        soup = self.request_(self.url+'/articles/')
        links = soup.find('div',{'id':'scrollingcontent'})
        for link in links.findAll('div',{'class':'listitem'}):
            self.company_list = []
            self.ticker_list = []
            self.par = []
            self.companies = {}
            self.price_d = {}
            self.link = self.url+link.find('a',href=True)['href']
            if self.link not in self.link_list:
                soup2 = self.request_(self.link)
                try:
                    header = soup2.find('header',{'class':'mugshot_large'})
                    title = header.find('h1')
                    author = header.find('p')
                    self.author = author.getText().split('by')[1].split(
                        'Published')[0].strip()
                    self.author = re.sub(r'[^\x00-\x7F]+','', self.author)
                    self.writer_check()
                    self.date = author.find('time').getText().strip()
                    self.date = datetime.strptime(self.date,'%B %d, %Y')
                    self.title = title.getText()
                    section = soup2.find('div',{'class':'commentary_body'})
                    for p in section.findAll('p'):
                        for name in p.findAll('strong'):
                            self.company_list.append(name.getText().split(
                                '(')[0].strip())
                        for ticker in p.findAll('span',{'class':'hoverquote-symbol'}):
                            self.ticker_list.append(ticker.getText())
                        line = re.sub(r'[^\x00-\x7F]+','',p.getText().lower(
                                    ).strip())
                        self.par.append(line)
                    self.all_prices()
                    self.db_lineUp()

                except AttributeError:
                    pass

    def theStreet(self):
        self.source = 'The Street'
        self.url = 'https://www.thestreet.com/'
        soup = self.request_(self.url+'stock-picks')
        for story in soup.findAll('div',{'class':'ks-paginator'}):
            count = 0
            for link in story.findAll('a',{'href':True}):
                count +=1
                bulk = (link.getText().strip())
                if len(bulk) == 0:
                    pass
                else:
                    if self.href_(link).startswith('/author'):
                        pass
                    else:
                        link2 = self.href_(link)
                        if link2.startswith('http://realmoney'):
                            url2 = link2
                        else:
                            url2 = self.url + link2
                        soup2 = self.request_(url2)
                        div = soup2.find('div',
                            {'class':'article__page article-standard__page'})
                        try:
                            self.ticker_list = []
                            self.company_list = []
                            self.par = []
                            self.companies = {}
                            self.price_d = {}
                            par = div.findAll('p')
                            for p in par:
                                try:
                                    for i in p.findAll('strong'):
                                        self.company_list.append(i.getText())
                                except AttributeError:
                                    pass
                                self.par.append(p.getText().lower())
                            for s in par:
                                try:
                                    tick = s.findAll('a')
                                    for t in tick:
                                        if len(t.getText().split(
                                            ' ')) <=1 and t.getText(
                                                )[0].isupper():
                                            self.ticker_list.append(
                                                t.getText())
                                except:
                                    pass
                            self.date = soup2.find('time',{'itemprop':
                                'datePublished'})
                            self.date = datetime.strptime(self.date.getText(
                                )[:-6].strip(),'%b %d, %Y %H:%M')
                        except:
                            tickers = soup2.find('div',{'class':'tickers'})
                            data = soup2.find('div',{'class':'content'})
                            date = soup2.find('div',{'class':'date'})
                            self.company_list = []
                            self.date = date.getText().split('|')[1].strip()
                            self.date = datetime.strptime(self.date,
                                '%b %d, %Y')
                            self.ticker_list = []
                            for ticker in tickers.findAll('h3'):
                                self.ticker_list.append(ticker.getText(
                                    ).upper())
                            self.par = []
                            for line in data.findAll('p'):
                                try:
                                    for i in line.findAll('strong'):
                                        self.company_list.append(i.getText(
                                            ).split('\xa0')[0].strip())
                                except AttributeError:
                                    pass
                                self.par.append(line.getText().lower())
                        self.title = soup2.title.getText()
                        self.link = url2
                        try:
                            self.author = soup2.find('span',
                                {'itemprop':'name'}).getText()
                            '''GET AUTHORS Writer ID if exists,
                            if does not exist, add to Writer DB'''
                        except:
                            try:
                                for author in soup2.findAll(
                                    'div',{'class':'author'}):
                                    if author.find('a'):
                                        self.author = author.find('a').getText()
                                        '''GET AUTHORS Writer ID if exists,
                                        if does not exist, add to Writer DB'''
                                        break
                            except:
                                print('error')
                        '''GATHERING TICKER MUST ENSURE
                                ITS THE RIGHT ONE!!!'''
                        self.all_prices()
                        self.db_lineUp()

    def request_(self,url,headers={'User-Agent':'''Mozilla/5.0
    (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)
    Chrome/33.0.1750.117 Safari/537.36''',}):
        try:
            request = urllib.request.Request(url,None,headers)
            response = urllib.request.urlopen(request)
            content = response.read()
            content = content.decode('UTF-8')
            return BeautifulSoup(content,'lxml')
        except:
            pass

    def href_(self,link):
        link = str(link)[str(link).find('href=')+6:]
        return link[:link.find('''"''')].strip()

    def sentences(self,key,name):
        self.keypar = []
        for sentence in self.par:
            if (name.lower().strip() in sentence):
                self.keypar.append(sentence)
            elif key.lower().strip() in sentence:
                self.keypar.append(sentence)
        self.keypar = ' '.join(self.keypar)

    def all_prices(self):
        if (self.date.month <datetime.today(
            ).month) or (self.date.day <
                datetime.today().day):
            for ticker in self.ticker_list:
                try:
                    self.company_name = self.comp_dict[ticker][0]
                    self.price = yahoo_price_(
                        symbol=ticker,date=self.date)
                    self.companies[ticker] = [self.company_name,self.price,
                        self.comp_dict[ticker][1]]
                except KeyError:
                    self.company_name,exchange = google_name(ticker)
                    self.company_name = name_clean(self.company_name)
                    print('for ticker: ',ticker,'\n',self.company_name,exchange)
                    if input('Do these look good?').startswith('n'):
                        print('Enter company name for: ', ticker)
                        self.company_name = input('Name: ')
                        print('This is Y!Fin, will ticker work?')
                        if input('(y/n)').startswith('n'):
                            ticker = input('New Y! Ticker: ')
                        if input('update exchange (y/n)').startswith('y'):
                            exchange = input('New exchange: ')
                    try:
                        self.price = yahoo_price_(
                            symbol=ticker,date=self.date)
                        self.companies[ticker] = [self.company_name,self.price,
                            exchange]
                        create_company(symbol=ticker,name=self.company_name,
                            sector='update',exchange=exchange)
                        self.comp_dict = company_dictionary()
                    except:
                        self.ticker_list.remove(ticker)
                        print('did not work: ',ticker)
        else:
            for ticker in self.ticker_list:
                try:
                    self.company_name = self.comp_dict[ticker][0]
                    self.price = google_price(ticker,self.comp_dict[ticker][1])
                    self.companies[ticker] = [self.company_name,self.price,
                        self.comp_dict[ticker][1]]
                except KeyError:
                    self.company_name,exchange = google_name(ticker)
                    if self.company_name == 'error':
                        print(self.company_name)
                    self.company_name = name_clean(self.company_name)
                    print('for ticker: ',ticker,'\n',self.company_name,exchange)
                    if input('Do these look good?').startswith('n'):
                        print('Enter company name for: ', ticker)
                        self.company_name = input('Name: ')
                        exchange = input('''Enter best exchange: ''')
                    try:
                        self.price = google_price(ticker,exchange)
                        self.companies[ticker] = [self.company_name,self.price,
                            exchange]
                        create_company(symbol=ticker,name=self.company_name,
                            sector='update',exchange=exchange)
                        self.comp_dict = company_dictionary()
                    except:
                        print('did not work: ',ticker)

    def db_lineUp(self):
        for key,value in self.companies.items():
            self.sentences(key,value[0])
            '''This is where we manually enter whether the article should
            enter the database or not based on whether the self.keypar
            is enough data to determine buy/sell'''
            # try:
            print('\nTitle: ',self.title,'by, ',
                self.author,'\n Written on: ',self.date,' @', self.link,
                '\nTicker: ',key,'| Company: ', value[0], '\n Trading at: ',
                    value[1],'on exchange: ',value[2],'\nArticle: ', self.keypar)
            side = True
            models.RawPost.create(
                link = self.link,
                side = side,
                symbol = key,
                title = self.title,
                entry_px = value[1],
                entry = self.keypar,
                writer = self.writer_id)

    def writer_dict_init(self):
        self.writer_dict = {}
        writers = models.Writer().select()
        for writer in writers:
            self.writer_dict[writer.name] = (writer.id,writer.company)

    def writer_create(self):
        models.Writer.create(
            name=self.author,
            company=self.source,
            bio=' ',
            website=self.url
        )
        self.writer_dict_init()
        self.writer_id = self.writer_dict[self.author][0]

    def writer_check(self):
        try:
            if self.writer_dict[self.author][1] == self.source:
                self.writer_id = self.writer_dict[self.author][0]
            else:
                self.writer_create()
        except:
            self.writer_create()

    def get_link(self):
        link_list = []
        for distinct in models.RawPost.select(models.RawPost.link).distinct():
            link_list.append(distinct.link)
        return link_list

webCrawl(['Jared Shulman'])
