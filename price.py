from bs4 import BeautifulSoup
import json
from urllib.request import urlopen

def price(ticker,exchange):
    link = "http://finance.google.com/finance/info?client=ig&q="
    try:
        url = link+"%s:%s" % (exchange,ticker)
        u = urlopen(url)
        content = u.read()
        content = content.decode('UTF-8')
        data = json.loads(content[3:])
        info = data[0]
        return float(info['l_fix'])
    except:
        return 0

def px_return(side,ep,cp):
    try:
        if side:
            return float(cp/ep-1)
        else:
            return float(ep/cp-1)
    except TypeError:
        return 0

class price_grab:
    def __init__(self,ticker_list,title,content):
        self.ticker_list = ticker_list
        self.title = title
        self.market_dict = {'TSE':'CA','TSX':'CA','NYSE':'US',
                        'NASDAQ':'US'}
        self.content = content
        self.name = None
        self.max = 0
        self.link = "http://finance.google.com/finance/info?client=ig&q="
        self._try_tickers()
    def _try_tickers(self):
        self.count = 0
        for ticker in self.ticker_list:
            for exchange in ['TSE','TSX','NYSE','NASDAQ']:
                try:
                    url = self.link+"%s:%s" % (exchange,ticker)
                    u = urlopen(url)
                    content = u.read()
                    content = content.decode('UTF-8')
                    data = json.loads(content[3:])
                    info = data[0]
                    self.cost =float(info['l_fix'])
                    self.ticker = ticker.strip()
                    self.exchange = exchange.strip()
                    self._name()
                except:
                    pass
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
        self.count = self.count + self.content.count(self.name.lower())
        short_name = self.name.split(' ')[:-1]
        if len(short_name) > 3:
            short_name = short_name[:-2]
            short_name = ' '.join(short_name).strip(',')
        else:
            short_name = ' '.join(short_name).strip(',')
        self.count = self.count + self.content.count(short_name.lower())
        if self.count > self.max:
            self.max = self.count
            market = self.market_dict[self.exchange]
            self.name_dict = {'name':self.name,'ticker':self.ticker,
                'exchange':self.exchange,'cost':self.cost,
                    'count':self.count,'market':market}
