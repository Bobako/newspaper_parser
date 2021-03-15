import requests
from bs4 import BeautifulSoup
import openpyxl
import time
from excel_writer import save_all
from threading import Thread
from threading_sys import Controller

def get_html(url):
    res =  requests.get(url)
    return res.text



def get_dates_links(url):
    html = get_html(url)
    url_start = 'https://www.ampravda.ru'
    
    soup = BeautifulSoup(html, 'lxml')

    links = soup.find('div', class_ = 'content').find_all('a')

    res = []
    
    for link in links:
        a = link.get('href')
        res.append(url_start+str(a))

    return res



def get_articles_links(url):
    html = get_html(url)
    
    url_start = 'https://www.ampravda.ru'
    
    soup = BeautifulSoup(html, 'lxml')

    links = soup.find('div', class_ = 'c-1').find_all('a')

    links += soup.find('div', class_ = 'column-1-1-1').find_all('a')

    
    res = []
    


    for link in links:
        if (link.get('class')!=['photo']) and (link.get('class')!=['rubric']):
            a = link.get('href')
            res.append(url_start+str(a))
                
 

    

    

    return res




    #article_example = {'id' = 0, 'datetime' = '', 'name' = '', 'category' = '','text' = ''}

def get_article(url):
    html = get_html(url)

    soup = BeautifulSoup(html, 'lxml')

    article = soup.find('article',id = 'article')
    
    try:
        name = article.find('h1').text
    except Exception:
        name = '' 
    try:
        category = article.find('a', class_ = 'rubric').text
    except Exception:
        category = ''
    try:
        article_text = article.find('section', class_= 'text')
    
    
        texts = article_text.find_all('p')
        fin_text = ''
        for text in texts:
            fin_text +=text.text
    except Exception:
        fin_text =''
    try:
        datetime = str(article.find('time', class_ = 'dt').get('datetime')).split(' ')[0]
    except Exception:
        datetime = ''
    return {'name' : name, 'category' : category, 'text' : fin_text, 'datetime' : datetime}

def get_period_articles_links(y1,y2):

    archives = []

    for i in range(y1,y2+1):
        archives.append(('https://www.ampravda.ru/archive/'+str(i)))


    dates = []
    for archive in archives:
        dates += get_dates_links(archive)
    
    articles_links = []

    for date in dates:
        articles_links+=get_articles_links(date)

    return articles_links

def get_articles(links):

    articles = []
    art_names = []

    for link in links:
        try:
            articles.append(get_article(link))
        except Exception:
            pass
    
    return articles
            

        

class MTP(Thread):

    links = []
    n = 0
    l = 0
    links_list=[]
    units = []
    fact_n = 0
    av_k = 0
    results = []
    
    def __init__(self,links,n = 10):
        self.links = links
        self.n = n
        self.l = len(links)

        print ('Запуск МПП')
        
        Thread.__init__(self)
        
        self.start()
        

    def divide_links(self):
        lpu = self.l//self.n  #links per unit

        r = []
        for i in range (self.n):
            r = self.links[lpu*i:lpu*(i+1)]
            self.links_list.append(r)
            r = []
            
        r = self.links[lpu*self.n:]
        if r!=[]:
            self.links_list.append(r)
        self.fact_n = len(self.links_list)
        
        
    def append_units(self):

        for i in range (self.fact_n):
            unit = MTP_unit(self.links_list[i])
            self.units.append(unit)



    def average_k(self):
        sum_k = 0
        for unit in self.units:
            sum_k +=unit.k

        av_k = sum_k/self.fact_n
        self.av_k = av_k
        return av_k

    def wait(self):
        while self.av_k!= 100:
            
            print('Готово на',self.average_k(), '%. Задействовано',self.count(),'потоков.')
            time.sleep(5)
            for unit in self.units:
                if unit.waiting == False:
                    self.results=unit.result
                    unit.result = []
                    if self.results == []:
                        unit.waiting = True
                    else:
                        save_all(self.results)
            
        print ('Завершено.')
        
    def count(self):
        counter = 0
        for unit in self.units:
            if unit.waiting == False:
                counter+=1
        return counter


    
 

    def run(self):
        self.divide_links()
        self.append_units()
        self.wait()

        
        
    

class MTP_unit(MTP):
    n = 0
    links = []
    i = 0
    parsed = 0
    k = 0
    result = []
    alive = True
    waiting = False
    
    
    def __init__(self,links):
        self.n = len(links)
        self.links = links

        Thread.__init__(self)
        
        self.start()


    def wait(self):
        while self.alive:
            time.sleep(1)
            
    def run(self):
        self.parsave()
        self.wait()

    def parsave(self):
       
        for i in range(len(self.links)):
            self.result.append(get_article(self.links[i]))
            self.k = (i+1)/self.n*100
            

#-----------------------------------------------------------------------------
st_tm = time.mktime(time.localtime())


links = get_period_articles_links(2016,2019)
l = len(links)
now = time.mktime(time.localtime())
print (now- st_tm, 'секунд. Получено ',l,'ссылок')

st_tm = time.mktime(time.localtime())
THR = Controller(100, links, get_article, save_all, 10)
