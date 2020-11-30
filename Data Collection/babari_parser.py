from bs4 import BeautifulSoup
import requests
from argparse import ArgumentParser
from database import ReplayDatabase
import time
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from numpy.random import rand
import matplotlib.pyplot as plt

from selenium import webdriver 
import matplotlib.pyplot as plt
# Taken from https://github.com/vasumv/pokemon_ai/tree/master/log_scraper

BABIRI_URL = "https://www.babiri.net/#/"
REPLAY_URL= "http://replay.pokemonshowdown.com/{replay_id}.log"

def parse_args():
    argparser = ArgumentParser()
    argparser.add_argument('db_path')
    return argparser.parse_args()

def get_teams():
    text = requests.get(BABIRI_URL)
    driver = webdriver.Chrome("/Users/aishwaryamustoori/Downloads/chromedriver")
    driver.get(BABIRI_URL)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    links = soup.find_all('div',{"class":"card-body"})
    all_teams = []
   
    for link in links : 
        team_list = list()
        images = link.find_all('img')
        for image in images:
            team_list.append(image.get('alt'))
        replay_id = link.find_all('a',{"class","card-link"})
        href = ""
        for replay in replay_id : 
            href = replay.get("href").strip("https://replay.pokemonshowdown.com/")
        if(len(team_list)==6) : 
            all_teams.append([team_list,href])

    return all_teams


def get_logs(replay_id):
    html = requests.get(REPLAY_URL.format(
        replay_id=replay_id)
    ).text
    return html

if __name__ == "__main__":
    args = parse_args()
    teams = get_teams() 
    teams_for_data_viz = {}
    r = ReplayDatabase(args.db_path)
    for team in teams:
        print ("Team: %s" % team)
        replay_id = team[1]
        for pokemon in team[0] : 
            if(teams_for_data_viz.get(pokemon)!=None): 
                teams_for_data_viz[pokemon] += 1
            else : 
                teams_for_data_viz[pokemon] = 1
        if r.check_team_replay_exists(team[1]):
            print ("Skipped Team: %s" % str(team[0]))
            continue
        print ("New replay ID: %s" % replay_id)
        r.add_team_replay(str(team[0]),replay_id, get_logs(replay_id))
        r.commit()
   
