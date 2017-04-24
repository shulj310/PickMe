from bs4 import BeautifulSoup
import json
import string
import urllib.request

def get_new_posts(username):
    url = '''http://www.fool.ca/recent-headlines/'''
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'
    headers = {'User-Agent':user_agent,}
    request = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    content = response.read()
    content = content.decode('UTF-8')
    soup = BeautifulSoup(content,'html.parser')
    count = 0
    update_dict = {}
    for a in soup.find_all('p'):
        count += 1
        if count%2 == 1:
            pass
        else:
            try:
                link=a.a.get('href')
                request = urllib.request.Request(link,None,headers)
                response = urllib.request.urlopen(request)
                content = response.read()
                content = content.decode('UTF-8')
                soup = BeautifulSoup(content,'html.parser')
                p = soup.find_all('p')
                paragraph = []
                for l in p:
                    text = (l.get_text())
                    text = str(text).lower().strip()
                    if text.find('more on') > 0:
                        name,date,ticker = (text.split('|'))
                        name,date,ticker = name.strip().title(),date.strip(),ticker.strip().split('more on:')[1].strip().upper()
                        ticker = list(ticker.split())
                        # if name in username:
                            # print('Name: ',name,'\nDate: ',date,'\nTicker: ',ticker)
                            # print('Link: ',link)
                    else:
                        # printable = set(string.printable)
                        # text = list(filter(lambda x: x in printable,text))
                        text = text.encode('ascii',errors='ignore')
                        text = text.decode('UTF-8')
                        paragraph.append(text)
                # print(paragraph)
                if name in username:
                    title = soup.title.get_text().split('|')[0].strip()
                    # print('Title: ',soup.title.get_text().split('|')[0])
                if name in username:
                    usecase = 'UseCase'+str(count)
                    paragraph = ' '.join(paragraph)
                    update_dict[usecase] = (name,date,ticker,link,title,paragraph)
            except:
                pass
    return update_dict


def teaser():
    url = '''http://www.fool.ca/recent-headlines/'''
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'
    headers = {'User-Agent':user_agent,}

    request = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    content = response.read()
    content = content.decode('UTF-8')
    soup = BeautifulSoup(content,'html.parser')
    a = soup.find_all('h2')
    title_list = []
    for z in a:
        title_list.append(z.get_text())
    return title_list
