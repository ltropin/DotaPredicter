from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
import json
driver = webdriver.PhantomJS('C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\handlers\\proxyParsers\\driver\\phantomjs')
# driver = webdriver.Chrome('driver\\chromedriver')
driver.get('https://free-proxy-list.net')


soup = BeautifulSoup(driver.page_source, 'lxml')
# Get number last page element in paginator
lastPage = len(soup.select('#proxylisttable_paginate > ul > li > a')) - 2
countPage = soup.select(f'#proxylisttable_paginate > ul > li:nth-child({lastPage}) > a')[0].get_text()
countPage = int(countPage)

# Get allNum page
proxyHttp = []
time.sleep(3)
for i in range(1, countPage + 1):
    driver.find_element_by_css_selector('#proxylisttable_next > a').click()
    soup = BeautifulSoup(driver.page_source, 'lxml')
    print(f'Go to page: {i}')
    # Get page for number page
    for row in soup.select('#proxylisttable > tbody > tr'):
        ipAddr = row.select('td:nth-child(1)')[0].get_text()
        port = row.select('td:nth-child(2)')[0].get_text()
        prox = {'http': f'http://{ipAddr}:{port}'}
        print(prox)
        proxyHttp.append(prox)

with open('C:/Users/1/Documents/PyProjects/DotaPredicter/handlers/proxyParsers/data/proxy2.json', 'w') as f:
    json.dump(proxyHttp, f, indent=4)

driver.close()