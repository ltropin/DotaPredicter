from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
from selenium import webdriver
import os
import json


req_session = requests.Session()
req_session.headers['X-API-TOKEN'] = 'QU5HTW91N2ZWSWxyOTZaU3tkOGFGWGJwVTFKJFlIaldAS3QweFR5aS13ZVBnY2tSNX0='
resp = req_session.get('https://proxies.su/proxies/api/?proxy_type=http&proxy_type=https').json()

data = []

for el in resp:
    data.append({el['proxy_type']: f'{el["proxy_type"]}://{el["ip"]}:{el["port"]}'})

with open('C:/Users/1/Documents/PyProjects/DotaPredicter/handlers/proxyParsers/data/proxy3.json', 'w') as f:
    json.dump(data, f, indent=4)