import json
import requests
from bs4 import BeautifulSoup
import random, string
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, '')
import django
from django.conf import settings
from pro.apps import ProConfig
sys.path.append('C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\dotapredicter')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dotapredicter.settings')
django.setup()
from pro.models import *
from django.core.files import File
import re
import time
BADCHARS = re.compile(r'[|\/<*?):]{1,}')
MODES_DB = ['captians_mode', 'all_pick']
DOTABUFF_URL = 'https://www.dotabuff.com'

SESSION = requests.session()
def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def get_random_proxy(proxyData):
    return random.choice(proxyData)


def get_heroes():
    urlHeroes = 'https://api.opendota.com/api/heroes'
    rawData = requests.get(urlHeroes).text
    jsonHeroes = json.loads(rawData)

    for hero in jsonHeroes:
        new_hero = Hero(id=hero['id'], name=hero['localized_name'])
        new_hero.save()
    print('All heroes parsed')


def get_players():
    urlPlayers = 'https://api.opendota.com/api/proPlayers'
    rawData = requests.get(urlPlayers).text
    jsonPlayers = json.loads(rawData)
    for player in jsonPlayers:
        contains_player = ProPlayer.objects.filter(id=player['account_id'])
        if len(contains_player) == 0:
            urlAva = player['avatarfull']
            
            player["name"] = BADCHARS.sub('', player["name"])
            pic = requests.get(urlAva, allow_redirects=True).content
            picName = 'avatars\\' + player["name"].replace(' ', '') + '_' + randomword(12) + '.png'
            with open(f'C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\pro\\media\\{picName}', 'wb') as f:
                f.write(pic)

            new_player = ProPlayer(id=player['account_id'],
                                steam_id=int(player['steamid']),
                                name=player["name"],
                                avatar=picName)
            new_player.save()
            print(player['name'])


def find_match(matcher, id_player):
    for p in matcher['players']:
        if p['account_id'] == id_player:
            return p


def get_data(url, proxylist, ua):
    current_ua = random.choice(ua)
    current_proxy = get_random_proxy(proxylist)
    print(f'User-Agent: {current_ua}')
    print(f'Proxy: {current_proxy}')
    return SESSION.get(url, headers={'User-Agent': current_ua}, proxies=current_proxy).json()


def get_html_data(url, proxylist, ua):
    # current_ua = random.choice(ua)
    current_ua = randomword(30)
    current_proxy = get_random_proxy(proxylist)
    # print(f'User-Agent: {current_ua}')
    print(f'Proxy: {current_proxy}')
    try:
        return SESSION.get(url, headers={'User-Agent': current_ua}, proxies=current_proxy, timeout=10).text
    except:
        return '<h2 id="status">Not Found</h2>'



def get_heroes_db(proxylist):
    url = 'https://www.dotabuff.com/heroes'
    data = get_html_data(url, proxylist)
    
    soup = BeautifulSoup(data, 'lxml')
    
    for el in soup.select('body > div.container-outer.seemsgood > div.container-inner.container-inner-content > div.content-inner > section:nth-child(3) > footer > div > a'):
        short_name = el.attrs['href'].split('/')[2]
        full_name = el.select_one('div > div.name').text
        print(full_name)
        url_picture = el.select_one('div').attrs['style'].split('(')[1][:-1]
        picture = requests.get(DOTABUFF_URL + url_picture).content
        picture_path = 'heroes\\' + short_name + '_' + randomword(15) + '.jpg'
        with open(f'C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\pro\\media\\{picture_path}', 'wb') as f:
            f.write(picture)
        new_hero = HeroDotaBuff(name=full_name,
                                short_name=short_name,
                                picture=picture_path)
        new_hero.save()

def find_hero(name):
    return HeroDotaBuff.objects.get(name=name)

def is_error_page(soup):
    return not(soup.select_one('#status') is None)

def get_user_agents():
    list_ua = []
    with open('C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\handlers\\proxyParsers\\data\\user-agents.txt', 'r') as f:
        for line in f.readlines():
            list_ua.append(line.replace('\n', ''))
    return list_ua

def get_proxy3():
    req_session = requests.Session()
    req_session.headers['X-API-TOKEN'] = 'QU5HTW91N2ZWSWxyOTZaU3tkOGFGWGJwVTFKJFlIaldAS3QweFR5aS13ZVBnY2tSNX0='
    resp = req_session.get('https://proxies.su/proxies/api/?proxy_type=http&proxy_type=https').json()

    data = []

    for el in resp:
        data.append({el['proxy_type']: f'{el["proxy_type"]}://{el["ip"]}:{el["port"]}'})

    return data

def save_file(data, file_name):
    with open(f'C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\handlers\\proxyParsers\\data\\{file_name}.txt', 'w') as f:
        print(data, file=f)

player_all = ProPlayer.objects.all()[1:]

# Fake User-Agents
user_agents = get_user_agents()

# Proxy file 1
jsonProxy2 = None
with open('C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\handlers\\proxyParsers\\data\\proxy.json', 'r') as f:
    jsonProxy2 = json.load(f)
# Proxy file 2
jsonProxy1 = None
with open('C:\\Users\\1\\Documents\\PyProjects\\DotaPredicter\\handlers\\proxyParsers\\data\\proxy2.json', 'r') as f:
    jsonProxy1 = json.load(f)

jsonProxy3 = get_proxy3()

resume = False

for player in player_all:
    player_url = f'https://www.dotabuff.com/players/{player.id}/heroes'
    print(f'URL hero: {player_url}')
    html_player = get_html_data(player_url, jsonProxy3, user_agents)
    soup_player = BeautifulSoup(html_player, 'lxml')
    
    # Infinity checking
    while is_error_page(soup_player):
        html_player = get_html_data(player_url, jsonProxy3, user_agents)
        soup_player = BeautifulSoup(html_player, 'lxml')
        time.sleep(10)
        jsonProxy3 = get_proxy3()
    list_hero = soup_player.select('body > div.container-outer.seemsgood > div.container-inner.container-inner-content > div.content-inner > section > article > table > tbody > tr > td.cell-xlarge > a')
    print(f'Count heroes: {len(list_hero)}')
    for hero_data in list_hero:
        hero_in_db = find_hero(hero_data.text)
        if resume or hero_in_db.name == 'Zeus':
            resume = True
            heroinfo_url = DOTABUFF_URL + hero_data.attrs['href']
            print(f'{hero_data.text} url: {heroinfo_url}')
            heroinfo_html = get_html_data(heroinfo_url, jsonProxy3, user_agents)
            try:

                heroinfo_soup = BeautifulSoup(heroinfo_html, 'lxml')
                # Infinity checking
                while is_error_page(heroinfo_soup):
                    heroinfo_html = get_html_data(heroinfo_url, jsonProxy3, user_agents)
                    heroinfo_soup = BeautifulSoup(heroinfo_html, 'lxml')
                    time.sleep(20)
                    jsonProxy3 = get_proxy3()
                
                time.sleep(5)
                # Count matches
                heroinfo_countmatches = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(1)')
                heroinfo_countmatches = int(heroinfo_countmatches.text.replace('Matches', ''))
                if heroinfo_countmatches <= 10:
                    break
                # Win rate
                heroinfo_winrate = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(3) > span').text
                heroinfo_winrate = float(heroinfo_winrate.replace('%', '')) / 100

                # Kills
                heroinfo_kills = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(5) > span').text
                heroinfo_kills = float(heroinfo_kills)

                # Deaths
                heroinfo_deaths = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(6) > span').text
                heroinfo_deaths = float(heroinfo_deaths)

                # Assists
                heroinfo_assists = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(7) > span').text
                heroinfo_assists = float(heroinfo_assists)

                # GPM
                heroinfo_GPM = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(8) > span').text
                heroinfo_GPM = int(heroinfo_GPM)

                # XPM
                heroinfo_XPM = heroinfo_soup.select_one('#match-aggregate-stats-target > div.r-stats-grid > div:nth-child(2) > div:nth-child(9) > span').text
                heroinfo_XPM = int(heroinfo_XPM)

                new_hero = HeroData(player=player,
                                    hero=hero_in_db,
                                    matches=heroinfo_countmatches,
                                    win_rate=heroinfo_winrate,
                                    kills=heroinfo_kills,
                                    deaths=heroinfo_deaths,
                                    assists=heroinfo_assists,
                                    GPM=heroinfo_GPM,
                                    XPM=heroinfo_XPM)
                new_hero.save()
                print(f'Hero - {hero_data.text} saved!')
            except:
                print(f'Error hero: {hero_in_db.id}, {hero_in_db}')
                save_file(str(heroinfo_html), hero_in_db.id)