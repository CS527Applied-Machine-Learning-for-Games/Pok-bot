import re
import json
from pathlib import Path
import sys
from database import ReplayDatabase
from collections import defaultdict
POKE = r"\|poke\|(?P<player>.+?)\|(?P<poke>.+?)\|"

SWITCH = r"\|(switch|drag)\|(?P<player>.+?)(a|b): (?P<nickname>.+?)\|(?P<pokename>.+)\|(?P<remainingHealth>.+)/(?P<totalHealth>.+)"
REPLACE = r"\|replace\|(?P<player>.+?)(a|b): (?P<nickname>.+?)\|(?P<pokename>.+?).+?"
MOVE = r"\|move\|(?P<player1>.+?)(a|b): (?P<poke1>.+?)\|(?P<move>.+?)\|(\[of\] )*(?P<player2>.+?)(a|b): (?P<poke2>.+)"
DAMAGE_MOVE = r"\|-damage\|(?P<player>.+?)(a|b): (?P<poke>.+?)\|(?P<remainingHealth>.+?)/(?P<totalHealth>.+)"
DAMAGE_FROM_FAINT_MOVE = r"\|-damage\|(?P<player>.+?)(a|b): (?P<poke>.+?)\|0 fnt\|\[from\] (?P<move>.+)"
DAMAGE_FROM_MOVE =  r"\|-damage\|(?P<player>.+?)(a|b): (?P<poke>.+?)\|(?P<remainingHealth>.+?)/(?P<totalHealth>.+?)\|\[from\] (?P<move>.+)"
DAMAGE_FAINT = r"\|-damage\|(?P<player>.+?)(a|b): (?P<poke>.+?)\|0 fnt"
DAMAGE_ITEM = r"\|-damage\|(?P<player>.+?)(a|b): (?P<poke>.+?)\|(?P<remainingHealth>.+?)/(?P<totalHealth>.+?)\|\[from\] item: (?P<item>.+)"
DAMAGE_ITEM_FAINT = r"\|-damage\|(?P<player>.+?)(a|b): (?P<poke>.+?)\|0 fnt\|\[from\] item :(?P<item>.+)"
SUPER_EFFECTIVE =  r"\|-supereffective\|(?P<player>.+?)(a|b): (?P<poke>.+)"

HEALTH =r"([a-zA-Z]+)(?P<health>[0-9]+).+?"
pokemon_health ={}
current_pokemon=''
move = ''
from_pokemon =''
to_pokemon=''
faint  = False
opponent_current_pokemon=''
graph_frequencies = {}
supereffective = {}
nick_names=defaultdict(str)
total_health={}
def handle_line(line):
    match = re.match(POKE, line)
    global current_pokemon
    global opponent_current_pokemon
    global from_pokemon
    global to_pokemon
    global move
    global faint
    if match:
        # Storing frequency of pokemon
        pokemon = match.group("poke").split(",")[0].split("-")[0]
        team[pokemon] +=1
        # graph_frequencies[pokemon] = dict()
        pokemon_health[pokemon]=0
    match = re.match(SWITCH, line)
    if match:
            
            nickname = match.group("nickname").split("-")[0]
            pokemon = match.group("pokename").split("-")[0].split(",")[0]
            
            if(nickname != ''):
                nick_names[nickname] = pokemon
            else :
                nick_names[pokemon] = pokemon
        
            main = match.group("remainingHealth").strip("(")
            pokemon_health[pokemon] = main
            if(total_health.get(pokemon) == None ):
                    total_health[pokemon] = main
            
            if (match.group("player") == "p1"  and current_pokemon=='') :
                current_pokemon = pokemon
            elif (match.group("player") =="p2"  and opponent_current_pokemon==''):
                opponent_current_pokemon = pokemon
            elif match.group("player") =="p1" and current_pokemon!="":
             
                if(graph_frequencies.get(current_pokemon) != None):
                    values = graph_frequencies[current_pokemon]
                    if(values.get('switch')==None):
                        graph_frequencies[current_pokemon]['switch'] = {"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon}
                    else:
                        graph_frequencies[current_pokemon]['switch'].update({"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon})
                else :
                    graph_frequencies[current_pokemon] = {"switch":{"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon}}
                current_pokemon = pokemon
            elif (match.group("player") =="p2" and opponent_current_pokemon!="") :
                if(graph_frequencies.get(opponent_current_pokemon) != None):
                    values = graph_frequencies[opponent_current_pokemon]
                    if(values.get('switch')==None):
                        graph_frequencies[opponent_current_pokemon]['switch'] = {"switchedPokemon":pokemon, "facingPokemon": current_pokemon}
                    else:
                        graph_frequencies[opponent_current_pokemon]['switch'].update({"switchedPokemon":pokemon, "facingPokemon": current_pokemon})
                else :
                    graph_frequencies[opponent_current_pokemon] = {"switch": {"switchedPokemon":pokemon, "facingPokemon": current_pokemon}}
                opponent_current_pokemon = pokemon
    match = re.match(REPLACE, line)
    if match:
            nickname = match.group("nickname")
            pokemon = match.group("pokename").split(",")[0].split("-")[0]
            if(nickname != ''):
                nick_names[nickname] = pokemon
            else :
                nick_names[pokemon] = pokemon
            if(not faint ):
                faint = False
                if (match.group("player") == "p1"  and current_pokemon=='') :
                    current_pokemon = pokemon
                elif (match.group("player") =="p2"  and opponent_current_pokemon==''):
                    opponent_current_pokemon = pokemon
                elif match.group("player") =="p1" and current_pokemon!="":
                    if(graph_frequencies.get(current_pokemon) != None):
                        values = graph_frequencies[current_pokemon]
                        if(values.get('switch')==None):
                            graph_frequencies[current_pokemon]['switch'] = {"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon}
                        else:
                            graph_frequencies[current_pokemon]['switch'].update({"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon})
                    else :
                        graph_frequencies[current_pokemon] = {"switch":{"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon}}
                    current_pokemon = pokemon
                elif (match.group("player") =="p2" and opponent_current_pokemon!="") :
                    if(graph_frequencies.get(opponent_current_pokemon) != None):
                        values = graph_frequencies[opponent_current_pokemon]
                        if(values.get('switch')==None):
                            graph_frequencies[opponent_current_pokemon]['switch'] = {"switchedPokemon":pokemon, "facingPokemon": current_pokemon}
                        else:
                            graph_frequencies[opponent_current_pokemon]['switch'].update({"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon})
                    else :
                        graph_frequencies[opponent_current_pokemon] = {"switch": {"switchedPokemon":pokemon, "facingPokemon": opponent_current_pokemon}}
                    opponent_current_pokemon = pokemon
            

    match = re.match(MOVE, line)
    if match:
        pokemon=match.group("poke1").split("-")[0]
        if(nick_names[pokemon]!= None):
            pokemon = nick_names[pokemon]
        else :
            nick_names[pokemon] = pokemon
        move = match.group("move").split("|")[0]
        from_pokemon = pokemon
        to_pokemon = match.group("poke2").split("-")[0].split("|")[0]
        if(graph_frequencies.get(pokemon) !=None):
            if(graph_frequencies[pokemon].get('moves') !=None):
                if(graph_frequencies[pokemon]['moves'].get(match.group("move"))!=None) :
                    graph_frequencies[pokemon]['moves'][match.group("move")] = graph_frequencies[pokemon]['moves'][match.group("move")]+1
                else :
                    graph_frequencies[pokemon]['moves'][match.group("move")] = 1
            else  :
                graph_frequencies[pokemon].update({"moves":{
                    match.group("move") : 1}})
        else :
            graph_frequencies[pokemon] = {"moves":{match.group("move"):1}}
    
    match = re.match(SUPER_EFFECTIVE, line)
    if(match) :
        pokemon = match.group("poke").split("-")[0]
        
        if(to_pokemon == nick_names[pokemon]) :
            if(supereffective.get(nick_names[from_pokemon]) != None) :
                supereffective[nick_names[from_pokemon]].update({"move":move,"fromPokemon" : pokemon})
            else :
                supereffective[nick_names[from_pokemon]] = {
                    "move":move,"fromPokemon" : pokemon
                }

    match = re.match(DAMAGE_ITEM_FAINT, line)
    if match :
            pokemon = match.group("poke").split("-")[0]
            item = match.group("item")
            if(graph_frequencies.get(nick_names[pokemon]) !=None):
                if(graph_frequencies[nick_names[pokemon]].get('damage') !=None):
                    graph_frequencies[nick_names[pokemon]]['damage']  =graph_frequencies[nick_names[pokemon]]['damage']  + [{"item":item,"damagePercent":"faint"}]
                else:
                    graph_frequencies[nick_names[pokemon]]['damage']= [{"item":item,"damagePercent":"faint"}]
            else:
                graph_frequencies[nick_names[pokemon]]={"damage":[{"item":item,"damagePercent":"faint"}]}
            faint = True
    else :
            match = match = re.match(DAMAGE_ITEM, line)
            if(match):
                pokemon = match.group("poke").split("-")[0]
                remainingHealth = match.group("remainingHealth").strip("(").strip(")").split(" ")
                totalHealth = match.group("totalHealth").strip("(").strip(")").split(" ")
                item = match.group("item").split("|")[0]
                                    
                if(len(remainingHealth)==2) :
                    remainingHealth = remainingHealth[1].strip("(")
                else :
                    remainingHealth= remainingHealth[0].strip("(")
                temp = re.compile("([0-9]+)([a-zA-Z]*)")
                totalHealth = re.match(temp,totalHealth[0]).groups()[0]
                if(pokemon_health.get(nick_names[pokemon]) != None) :
                    strip = str(pokemon_health[nick_names[pokemon]]).strip(" ").strip("(").strip(")")
                else :
                    strip = totalHealth
                percentageDamage =((int(strip)-int(remainingHealth)) /int(totalHealth)) *100
                if(graph_frequencies.get(nick_names[pokemon]) !=None):
                    if(graph_frequencies[nick_names[pokemon]].get('damage') !=None):
                        graph_frequencies[nick_names[pokemon]]['damage']  =graph_frequencies[nick_names[pokemon]]['damage']  + [{"item":item,"damagePercent":percentageDamage}]
                    else:
                        graph_frequencies[nick_names[pokemon]]['damage']= [{"item":item,"damagePercent":percentageDamage}]
                else:
                    graph_frequencies[nick_names[pokemon]]={"damage":[{"item":item,"damagePercent":percentageDamage}]}
            else :
                    match = re.match(DAMAGE_FROM_MOVE, line)
                    if match :
                        pokemon = match.group("poke").split("-")[0]
                        move1 = match.group("move").split("|")[0]
                        remainingHealth = match.group("remainingHealth").strip("(").strip(")").split(" ")
                        totalHealth = match.group("totalHealth").strip("(").strip(")").split(" ")
                        if(len(remainingHealth)==2) :
                            remainingHealth = remainingHealth[1].strip("(")
                        else :
                            remainingHealth= remainingHealth[0].strip("(")
                            temp = re.compile("([0-9]+)([a-zA-Z]*)")
                            totalHealth = re.match(temp,totalHealth[0]).groups()[0]
                                            
                            if(pokemon_health.get(nick_names[pokemon]) != None) :
                                strip = str(pokemon_health[nick_names[pokemon]]).strip(" ").strip("(").strip(")")
                            else :
                                strip = totalHealth
                            percentageDamage =((int(strip)-int(remainingHealth)) /int(totalHealth)) *100
                            if(graph_frequencies.get(nick_names[pokemon]) !=None):
                                if(graph_frequencies[nick_names[pokemon]].get('damage') !=None):
                                    graph_frequencies[nick_names[pokemon]]['damage']  =graph_frequencies[nick_names[pokemon]]['damage']  + [{"move":move1,"damagePercent":percentageDamage}]
                                else:
                                    graph_frequencies[nick_names[pokemon]]['damage']= [{"move":move1,"damagePercent":percentageDamage}]
                            else:
                                graph_frequencies[nick_names[pokemon]]={"damage":[{"move":move1,"damagePercent":percentageDamage}]}
                        
                    else :
                        match = re.match(DAMAGE_FROM_FAINT_MOVE, line)
                        if(match):
                            pokemon = match.group("poke").split("-")[0]
                            move1 = match.group("move").split("|")[0]
                            if(graph_frequencies.get(nick_names[pokemon]) !=None):
                                if(graph_frequencies[nick_names[pokemon]].get('damage') !=None):
                                    graph_frequencies[nick_names[pokemon]]['damage']  =graph_frequencies[nick_names[pokemon]]['damage']  + [{"move":move1,"damagePercent":"faint"}]
                                else:
                                    graph_frequencies[nick_names[pokemon]]['damage']= [{"move":move1,"damagePercent":"faint"}]
                            else:
                                graph_frequencies[nick_names[pokemon]]={"damage":[{"move":move1,"damagePercent":"faint"}]}
                            faint = True
                        else :
                            match = re.match(DAMAGE_FAINT, line)
                            if match :
                                pokemon = match.group("poke").split("-")[0]
                                percentageDamage= 0
                                if(graph_frequencies.get(nick_names[pokemon]) !=None):
                                    if(graph_frequencies[nick_names[pokemon]].get('damage') !=None):
                                        graph_frequencies[nick_names[pokemon]]['damage']  =graph_frequencies[nick_names[pokemon]]['damage']  + [{"move":move,"fromPokemon":from_pokemon,"damagePercent":"faint"}]
                                    else:
                                        graph_frequencies[nick_names[pokemon]]['damage']= [{"move":move,"fromPokemon":from_pokemon,"damagePercent":"faint"}]
                                else:
                                    graph_frequencies[nick_names[pokemon]]={"damage":[{"move":move,"fromPokemon":from_pokemon,"damagePercent":"faint"}]}
                                if(to_pokemon == pokemon):
                                    move = ""
                                faint = True
                            else :
                                    match = match = re.match(DAMAGE_MOVE, line)
                                    if(match):
                                        pokemon = match.group("poke").split("-")[0]
                                        remainingHealth = match.group("remainingHealth").strip("(").strip(")").split(" ")
                                        totalHealth = match.group("totalHealth").strip("(").strip(")").split(" ")
                                        
                                        if(len(remainingHealth)==2) :
                                            remainingHealth = remainingHealth[1].strip("(")
                                        else :
                                            remainingHealth= remainingHealth[0].strip("(")
                                        temp = re.compile("([0-9]+)([a-zA-Z]*)")
                                        totalHealth = re.match(temp,totalHealth[0]).groups()[0]
                                        
                                        
                                        if(pokemon_health.get(nick_names[pokemon]) != None) :
                                            strip = str(pokemon_health[nick_names[pokemon]]).strip(" ").strip("(").strip(")")
                                        else :
                                            strip = totalHealth
                                        percentageDamage =((int(strip)-int(remainingHealth)) /int(totalHealth)) *100
                                        if(graph_frequencies.get(nick_names[pokemon]) !=None):
                                            if(graph_frequencies[nick_names[pokemon]].get('damage') !=None):
                                                graph_frequencies[nick_names[pokemon]]['damage'].append({"move":move,"fromPokemon":from_pokemon,"damagePercent":percentageDamage})
                                            else:
                                                graph_frequencies[nick_names[pokemon]]['damage']= [{"move":move,"fromPokemon":from_pokemon,"damagePercent":percentageDamage}]
                                        else:
                                            graph_frequencies[nick_names[pokemon]]={"damage":[{"move":move,"fromPokemon":from_pokemon,"damagePercent":percentageDamage}]}
                                        if(to_pokemon == pokemon):
                                            move = ""


         
if __name__ == "__main__":
    supereffective ={}
    r = ReplayDatabase(sys.argv[0])
    names = r.select_all_replays()
    index = 0
    team = defaultdict(int)
    for username in names:
        directory = username
        current_pokemon=''
        move = ''
        from_pokemon =''
        to_pokemon=''
        
        faint  = False
        opponent_current_pokemon=''
        for log in directory[2].split("\n"):
            index = index+1
            lines = log.split("\n")
            for line in lines:
                handle_line(line)
        
    poke_graph = {
        'Replay Data': graph_frequencies,
        'Team Frequences': team,
        'Super Effective Moves':supereffective
    }
    with open("ans.json", "w") as f:
        f.write(json.dumps(poke_graph, sort_keys=True,indent=4, separators=(',', ': ')))

