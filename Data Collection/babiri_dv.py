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
if __name__ == "__main__":
    teams = get_teams() 
    teams_for_data_viz = {}
    for team in teams:
        print ("Team: %s" % team)
        replay_id = team[1]
        for pokemon in team[0] : 
            if(teams_for_data_viz.get(pokemon)!=None): 
                teams_for_data_viz[pokemon] += 1
            else : 
                teams_for_data_viz[pokemon] = 1
    all_lists = sorted(teams_for_data_viz.items(),key = lambda x :x[1],reverse=True)[:10]
    
    x_labels = [x[0] for x in all_lists]
   
    frequencies =  [x[1] for x in all_lists]
    freq_series = pd.Series(frequencies)

    
    plt.figure(figsize=(40, 30))
    plt.rcParams.update({'font.size': 45})
    my_cmap = cm.get_cmap('jet')
    my_norm = Normalize(vmin=0, vmax=41)

    ax = freq_series.plot(kind='bar',color=my_cmap(my_norm(frequencies)))
    ax.set_title('Usage of Pokemon')
    ax.set_xlabel('Pokemon')
    ax.set_ylabel('Usage')
    ax.set_xticklabels(x_labels,rotation=45, horizontalalignment='right')


    

    def add_value_labels(ax, spacing=10):

        for rect in ax.patches:
            y_value = rect.get_height()
            x_value = rect.get_x() + rect.get_width() / 2

            space = spacing
            va = 'bottom'

            if y_value < 0:
                space *= -1
                va = 'top'
            label = "{:.1f}".format(y_value)

            ax.annotate(
                label,                    
                (x_value, y_value),       
                xytext=(0, space),          
                textcoords="offset points", 
                ha='center',               
                va=va)                      
                                            

    add_value_labels(ax)

    plt.savefig("image.png")