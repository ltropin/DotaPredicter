from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
from selenium import webdriver
import os
import json
driver = webdriver.PhantomJS('C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\handlers\\proxyParsers\\driver\\phantomjs')
# driver = webdriver.Chrome('driver\\chromedriver')
driver.get('https://hidemyna.me/en/proxy-list/?maxtime=1600&type=hs')
time.sleep(10)

soup = BeautifulSoup(driver.page_source, 'lxml')

countPages = len(soup.select('#content-section > section.proxy > div > div.proxy__pagination > ul > li'))
numCountPages = soup.select(f'#content-section > section.proxy > div > div.proxy__pagination > ul > li:nth-child({countPages}) > a')[0].get_text()
print(f'Колво страниц: {numCountPages}')
proxyHttp = []
for i in range(int(numCountPages)):
    urlNext = f'https://hidemyna.me/en/proxy-list/?maxtime=1600&type=hs&start={64 * i}'
    print(f'Go: {urlNext}')
    driver.get(urlNext)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    print(f'Page: {i + 1}')
    for row in soup.select('#content-section > section.proxy > div > table > tbody > tr'):
        ipRow = row.select('td:nth-child(1)')[0].get_text()
        port = row.select('td:nth-child(2)')[0].get_text()
        print(f'{ipRow}:{port}')
        proxyHttp.append(f'{ipRow}:{port}')
proxyDict = [{'http': f'http://{el}'} for el in proxyHttp]
with open('C:/Users/1/Documents/PyProjects/DotaPredicter/handlers/proxyParsers/data/proxy.json', 'w') as f:
    json.dump(proxyDict, f, indent=4)
# proxData = pd.DataFrame({'HTTP': proxyHttp})
# proxData.to_csv('C:/Users/1/Documents/PyProjects/DotaPredicter/handlers/proxyParsers/data/proxylist1.csv')
driver.close()