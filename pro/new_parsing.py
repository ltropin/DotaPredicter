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
API_STEAM_KEY  = '5FCA2D998706DDA5E38D09F23AB660C1'
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
    # current_ua = random.choice(ua)
    current_ua = randomword(30)
    current_proxy = get_random_proxy(proxylist)
    print(f'Proxy: {current_proxy}')
    try:
        # headers={'User-Agent': current_ua}, proxies=current_proxy,
        return requests.get(url, timeout=10).json()
    except:
        return 'error'



def get_html_data(url, proxylist, ua):
    # current_ua = random.choice(ua)
    current_ua = randomword(30)
    current_proxy = get_random_proxy(proxylist)
    # print(f'User-Agent: {current_ua}')
    print(f'Proxy: {current_proxy}')
    try:
        return SESSION.get(url, headers={'User-Agent': current_ua}, proxies=current_proxy, timeout=10).text
    except:
        return 'error'


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

def find_player(json_list, player_id):
    for el in json_list:
        if el['account_id'] == player_id:
            return el

player_all = ProPlayer.objects.all()

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

# jsonProxy3 = get_proxy3()

CMatch.objects.all().delete()
SimpleMatch.objects.all().delete()
HeroData.objects.all().delete()
MatchInfo.objects.all().delete()

for player in player_all:
    url_history = f'https://api.opendota.com/api/players/{player.id}/matches?api_key=004a3115-0163-48cd-b804-0e22ecca5cfb'
    print(f'URL history: {url_history}')
    # json_player = get_data(url_history, jsonProxy3, user_agents)
    json_player = requests.get(url_history).json()
    if json_player != 'error':
        # Infinity checking
        json_player = requests.get(url_history).json()
        # while 'error' in json_player:
        #     json_player = get_data(url_history, jsonProxy3, user_agents)
        #     time.sleep(10)
        #     jsonProxy3 = get_proxy3()
        match_ids_hero = {}

        for match in json_player:
            if not(match['hero_id'] in match_ids_hero):
                match_ids_hero[match['hero_id']] = []
            match_ids_hero[match['hero_id']].append(match['match_id'])

        # resume = player.id != 88470
        resume = True
        added = False
        for hero_id, match_list in match_ids_hero.items():
            avg_data = {
                'matches': 0,
                'wins': 0,
                'kills': [],
                'deaths': [],
                'assists': [],
                'GPM': [],
                'XPM': []
            }   
            try:
                if len(match_list) < 10:
                    continue
                hero_db = Hero.objects.get(pk=hero_id)
                print(f'ID: {hero_db.id}, {hero_db.name}')
                if resume or hero_db.id == 97:
                    if not(resume):
                        resume = True
                        continue
                    resume = True
                    print(f'Count matches: {len(match_list)}')
                    for iv, match_id in enumerate(match_list):
                        # url_details = f'https://api.opendota.com/api/matches/{match_id}?api_key=004a3115-0163-48cd-b804-0e22ecca5cfb'
                        url_details = f'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/?match_id={match_id}&key={API_STEAM_KEY}'
                        print(f'{iv + 1}) URL details: {url_details}')
                        json_details = requests.get(url_details).json()

                        if json_details != 'error':
                            heroinfo = find_player(json_details['result']['players'], player.id)
                            json_details = json_details['result']
                            # Save data for Captians Mode
                            try:
                                if json_details['game_mode'] == 2 and len(json_details['picks_bans']) == 22:
                                    for pick_ban in json_details['picks_bans']:
                                        pb_hero = Hero.objects.get(pk=pick_ban['hero_id'])
                                        competitve_match = CMatch(match_id=match_id, hero=pb_hero, player_id=simple_hero['account_id'], is_pick=pick_ban['is_pick'])
                                        competitve_match.save()
                                    print(f'Competitve match {match_id} saved')
                                elif json_details['human_players'] == 10:
                                    for simple_hero in json_details['players']:
                                        sm_hero = Hero.objects.get(pk=simple_hero['hero_id'])
                                        sm = SimpleMatch(match_id=match_id, hero=sm_hero, player_id=simple_hero['account_id'])
                                        sm.save()
                            except Exception as e:
                                print('Error save match info')
                                print(e)

                            avg_data['kills'].append(heroinfo['kills'])
                            avg_data['deaths'].append(heroinfo['deaths'])
                            avg_data['assists'].append(heroinfo['assists'])
                            avg_data['GPM'].append(heroinfo['gold_per_min'])
                            avg_data['XPM'].append(heroinfo['xp_per_min'])
                            # Saving match info
                            if 'lobby_type' in json_details.keys() and 'game_mode' in json_details.keys():
                                new_matchinfo = MatchInfo(match_id=match_id,
                                                        lobby_type=json_details['lobby_type'],
                                                        game_mode=json_details['game_mode'])
                                new_matchinfo.save()

                    new_hero = HeroData(player=player,
                                        hero=hero_db,
                                        matches=len(match_list),
                                        kills=np.average(avg_data['kills']),
                                        deaths=np.average(avg_data['deaths']),
                                        assists=np.average(avg_data['assists']),
                                        GPM=np.average(avg_data['GPM']),
                                        XPM=np.average(avg_data['XPM']))
                    new_hero.save()

                    print(f'Hero {hero_db.name} saved!')
            except Exception as e:
                print(f'Error hero: {hero_id}')
                save_file(str(e), hero_id)