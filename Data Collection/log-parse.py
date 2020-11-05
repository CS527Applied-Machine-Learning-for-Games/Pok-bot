import re
import json
from pathlib import Path
import sys
from database import ReplayDatabase
from collections import defaultdict
POKE = r"\|poke\|(?P<player>.+?)\|(?P<poke>.+?)\|"
USER_PLAYER = r"\|player\|(?P<player>.+?)\|(?P<username>.+?)\|.*?"
TURN =  r"\|turn\|(?P<turnNumber>.+?)"
SWITCH = r"\|(switch|drag)\|(?P<player>.+?)(a|b|c): (?P<nickname>.+?)\|(?P<pokename>.+)\|(?P<remainingHealth>.+)/(?P<totalHealth>.+)"
REPLACE = r"\|replace\|(?P<player>.+?)(a|b|c): (?P<nickname>.+?)\|(?P<pokename>.+?).+?"
SWAP = r"\|swap\|(?P<player>.+?)(a|b|c): (?P<pokename>.+?)\|.+?"
MOVE = r"\|move\|(?P<player1>.+?)(a|b|c): (?P<poke1>.+?)\|(?P<move>.+?)\|(\[of\] )*(?P<player2>.+?)(a|b|c): (?P<poke2>.+)"
DAMAGE_MOVE = r"\|-damage\|(?P<player>.+?)(a|b|c): (?P<poke>.+?)\|(?P<remainingHealth>.+?)/(?P<totalHealth>.+)"
DAMAGE_FROM_FAINT_MOVE = r"\|-damage\|(?P<player>.+?)(a|b|c): (?P<poke>.+?)\|(0 fnt|0)\|\[from\] (?P<move>.+)"
DAMAGE_FROM_MOVE =  r"\|-damage\|(?P<player>.+?)(a|b|c): (?P<poke>.+?)\|(?P<remainingHealth>.+?)/(?P<totalHealth>.+?)\|\[from\] (?P<move>.+)"
DAMAGE_FAINT = r"\|-damage\|(?P<player>.+?)(a|b|c): (?P<poke>.+?)\|(0 fnt|0)"
DAMAGE_ITEM = r"\|-damage\|(?P<player>.+?)(a|b|c): (?P<poke>.+?)\|(?P<remainingHealth>.+?)/(?P<totalHealth>.+?)\|\[from\] item: (?P<item>.+)"
DAMAGE_ITEM_FAINT = r"\|-damage\|(?P<player>.+?)(a|b|c): (?P<poke>.+?)\|(0 fnt|0)\|\[from\] item :(?P<item>.+)"
WIN =  r"\|win\|(?P<player>.+)"
FORFEIT = r"\|-message\|(?P<player>.+) forfeited."
HEALTH =r"([a-zA-Z]+)(?P<health>[0-9]+).+?"
STATUS =  r"\|-status\|(?P<player>.+?)(a|b|c): (?P<pokename>.+?)\|.*?"
CURESTATUS =  r"\|-curestatus\|(?P<player>.+?)(a|b|c): (?P<pokename>.+?)\|.*?"

healthOne = {}
healthTwo ={}
nick_names ={}
team1 = []
team2 =[]
team1pokemon = []
team2pokemon = []
user1 = ''
user2 = ''
    
noOfTeam1Pokemon = 0 
noOfTeam2Pokemon = 0 
    
noOfFaintedPokemonForTeam1=0 
noOfFaintedPokemonForTeam2=0
turn = 1
ans = []
def handle_line(lines):
    global noOfTeam1Pokemon 
    global noOfTeam2Pokemon 
    global teamOneHealth
    global teamTwoHealth 
    global ans  
    global noOfFaintedPokemonForTeam1 
    global noOfFaintedPokemonForTeam2
    global turn
    global noofStatsPokemon1 
    global noofStatsPokemon2
    global statsTeam1 
    global statsTeam2
    for line in lines:
        # print(line)
        match = re.match(USER_PLAYER, line)
        if match:
            player = match.group("player")
            nickname = match.group("username")
            if("p1" in player):
                user1 = nickname
            else:
                user2 = nickname
            continue
        match = re.match(STATUS, line)
        if match:
            player = match.group("player")
            pokemon = match.group("pokename").split("-")[0]
            if(pokemon == ''):
                pokemon = match.group("pokename")

            if("p1" in player and  pokemon not in statsTeam1):
                noofStatsPokemon1 +=1
                statsTeam1.append(pokemon)
            else:
                if(pokemon not in statsTeam2):
                    noofStatsPokemon2 +=1
                    statsTeam2.append(pokemon)
            continue
        match = re.match(CURESTATUS, line)
        if match:
            
            player = match.group("player")
            pokemon = match.group("pokename").split("-")[0]
            if("p1" in player and  pokemon not in statsTeam1):
                noofStatsPokemon1 +=1
                statsTeam1.append(pokemon)
            else:
                if(pokemon not in statsTeam2):
                    noofStatsPokemon2 +=1
                    statsTeam2.append(pokemon)
            continue
        
        match = re.match(FORFEIT,line)
        if match : 
            player = match.group("player")
            if(len(healthOne) !=0 and len(healthTwo) != 0):
                teamOneHealth = sum(healthOne.values())+ 100 * (6-len(healthOne.values()))
                teamTwoHealth = sum(healthTwo.values())+ 100 * (6-len(healthTwo.values()))
                
                team1.append([turn,noOfTeam1Pokemon,noOfFaintedPokemonForTeam1,noofStatsPokemon1,teamOneHealth])
                team2.append([turn,noOfTeam2Pokemon,noOfFaintedPokemonForTeam2,noofStatsPokemon2,teamTwoHealth])
                if("p2" in player):
                    ans = ["for",team1,team2]
                    break
                else:
                    ans =  ["for",team2,team1]
                    break
            else:
                ans = []

        match = re.match(WIN,line)
        if match : 
            # print('ee11')
            player = match.group("player")
            if(len(healthOne) !=0 and len(healthTwo) != 0):
                
                teamOneHealth = sum(healthOne.values())+ 100* (6-len(healthOne.values()))
                teamTwoHealth = sum(healthTwo.values())+ 100* (6-len(healthTwo.values()))
                team1.append([turn,noOfTeam1Pokemon,noOfFaintedPokemonForTeam1,noofStatsPokemon1,teamOneHealth])
                team2.append([turn,noOfTeam2Pokemon,noOfFaintedPokemonForTeam2,noofStatsPokemon2,teamTwoHealth])
                
                if("p1" in player):
                    ans = ["win",team1,team2]
                    break
                else:
                    ans =  ["win",team2,team1]
                    break
            else:
                ans = []

        match = re.match(TURN, line)
        if(match): 
            
            if(len(healthOne) !=0 and len(healthTwo) != 0):
                teamOneHealth = sum(healthOne.values()) + 100* (6-len(healthOne.values()))
                teamTwoHealth = sum(healthTwo.values())+ 100* (6-len(healthTwo.values()))
                
            else: 
                teamOneHealth = 600
                teamTwoHealth = 600 
            
            team1.append([turn,noOfTeam1Pokemon,noOfFaintedPokemonForTeam1,noofStatsPokemon1,teamOneHealth])
            team2.append([turn,noOfTeam2Pokemon,noOfFaintedPokemonForTeam2,noofStatsPokemon2,teamTwoHealth])
            turn +=1
            continue
        match = re.match(SWITCH, line)
        if match:
                nickname = match.group("nickname")
                
                pokemon = match.group("pokename").split("-")[0].split(",")[0]
                if(pokemon == ''):
                    pokemon = match.group("pokename")
                
                player = match.group("player")
                totalHealth = match.group("totalHealth").strip("(").strip(")").strip(" ")
                remainingHealth = match.group("remainingHealth").strip(")").strip(" ").strip("(")
                
                
                if(totalHealth == remainingHealth):
                    if("p1" in player):
                        healthOne[nickname] = 100
                    else : 
                        healthTwo[nickname] = 100

                if(nickname != ''):
                    nick_names[nickname] = pokemon
                else : 
                    nick_names[pokemon] = pokemon
                # print(healthOne)    
                if("p1" in player):
                    if(nickname not in team1pokemon):
                        noOfTeam1Pokemon += 1 
                        team1pokemon.append(nickname)
                else : 
                    if(nickname not in team2pokemon):
                        noOfTeam2Pokemon += 1 
                        team2pokemon.append(nickname)
                continue

        match = re.match(REPLACE, line) 
        if match:
                nickname = match.group("nickname")
                pokemon = match.group("pokename").split("-")[0].split(",")[0]
                if(pokemon == ''):
                    pokemon = match.group("pokename")
                player = match.group("player")
      
                if("p1" in player):
                    healthOne[nickname] = 100
                else : 
                    healthTwo[nickname] = 100

                if(nickname != ''):
                    nick_names[nickname] = pokemon
                else : 
                    nick_names[pokemon] = pokemon

                if("p1" in player):
                    if(nickname not in team1pokemon):
                        noOfTeam1Pokemon += 1 
                        team1pokemon.append(nickname)
                else : 
                    if(nickname not in team2pokemon):
                        noOfTeam2Pokemon += 1 
                        team2pokemon.append(nickname)
                continue
        match = re.match(SWAP, line) 
        if match:
                
                pokemon = match.group("pokename").split("-")[0].split(",")[0]
                if(pokemon == ''):
                    pokemon = match.group("pokename")
                player = match.group("player")
                
                if("p1" in player):
                    healthOne[pokemon] = 100
                else : 
                    healthTwo[pokemon] = 100
                
                nick_names[pokemon] = pokemon

                if("p1" in player):
                    if(pokemon not in team1pokemon):
                        noOfTeam1Pokemon += 1 
                        team1pokemon.append(pokemon)
                else : 
                    if(pokemon not in team2pokemon):
                        noOfTeam2Pokemon += 1 
                        team2pokemon.append(pokemon)
                continue

        match = re.match(DAMAGE_ITEM_FAINT, line) 
        if match : 
                pokemon = match.group("poke")
                if(pokemon ==''):
                    pokemon= match.group("poke")
                nickname = nick_names[pokemon]
                player = match.group("player")
                if("p1" in player): 
                    healthOne[nickname] = 0
                    noOfFaintedPokemonForTeam1 +=1
                else : 
                    healthTwo[nickname] = 0 
                    noOfFaintedPokemonForTeam2 +=1
                continue
        else : 
                
                match = match = re.match(DAMAGE_ITEM, line) 
                if(match):
                    pokemon = match.group("poke")
                    if(pokemon ==''):
                        pokemon= match.group("poke")
                    remainingHealth = match.group("remainingHealth").strip("(").strip(")").split(" ")
                    totalHealth = match.group("totalHealth").strip("(").strip(")").split(" ")
                    
                    if(len(remainingHealth)==2) : 
                        remainingHealth = remainingHealth[1].strip("(")
                    else : 
                        remainingHealth= remainingHealth[0].strip("(")
                    temp = re.compile("([0-9]+)([a-zA-Z]*)") 
                    totalHealth = re.match(temp,totalHealth[0]).groups()[0]
                     
                    percentageDamage =((int(totalHealth)-int(remainingHealth)) /int(totalHealth)) *100 
                    
                    nickname = nick_names[pokemon]
                    player = match.group("player")
                    if("p1" in player): 
                        healthOne[nickname] = percentageDamage
                    else : 
                        healthTwo[nickname] = percentageDamage
                    continue
                else :
                          
                        match = match = re.match(DAMAGE_ITEM, line) 
                        if(match):
                            pokemon = match.group("poke")
                            if(pokemon ==''):
                                pokemon= match.group("poke")
                            remainingHealth = match.group("remainingHealth").strip("(").strip(")").split(" ")
                            totalHealth = match.group("totalHealth").strip("(").strip(")").split(" ")
                            
                            if(len(remainingHealth)==2) : 
                                remainingHealth = remainingHealth[1].strip("(")
                            else : 
                                remainingHealth= remainingHealth[0].strip("(")
                            temp = re.compile("([0-9]+)([a-zA-Z]*)") 
                            totalHealth = re.match(temp,totalHealth[0]).groups()[0]
                            
                            percentageDamage =((int(totalHealth)-int(remainingHealth)) /int(totalHealth)) *100 
                            
                            nickname = nick_names[pokemon]
                            player = match.group("player")
                            if("p1" in player): 
                                healthOne[nickname] = percentageDamage
                            else : 
                                healthTwo[nickname] = percentageDamage
                            continue
                        else :
                            
                            match = re.match(DAMAGE_FROM_FAINT_MOVE, line) 
                            if(match): 
                                pokemon = match.group("poke")
                                if(pokemon ==''):
                                    pokemon= match.group("poke")
                                nickname = nick_names[pokemon]
                                player = match.group("player")
                                if("p1" in player): 
                                    healthOne[nickname] = 0
                                    noOfFaintedPokemonForTeam1 +=1
                                else : 
                                    healthTwo[nickname] = 0 
                                    noOfFaintedPokemonForTeam2 +=1
                                continue
                            else :
                                
                                match = re.match(DAMAGE_FAINT, line) 
                                if match : 
                                    pokemon = match.group("poke")
                                    if(pokemon ==''):
                                        pokemon= match.group("poke")
                                    nickname = nick_names[pokemon]
                                    player = match.group("player")
                                    if("p1" in player): 
                                        healthOne[nickname] = 0
                                        noOfFaintedPokemonForTeam1 +=1
                                    else : 
                                        healthTwo[nickname] = 0 
                                        noOfFaintedPokemonForTeam2 +=1
                                    continue
                                else : 
                                        
                                        match = match = re.match(DAMAGE_MOVE, line) 
                                        if(match):
                                            pokemon = match.group("poke")
                                            if(pokemon ==''):
                                                pokemon= match.group("poke")
                                            remainingHealth = match.group("remainingHealth").strip("(").strip(")").split(" ")
                                            totalHealth = match.group("totalHealth").strip("(").strip(")").split(" ")
                                            
                                            if(len(remainingHealth)==2) : 
                                                remainingHealth = remainingHealth[1].strip("(")
                                            else : 
                                                remainingHealth= remainingHealth[0].strip("(")
                                            temp = re.compile("([0-9]+)([a-zA-Z]*)") 
                                            totalHealth = re.match(temp,totalHealth[0]).groups()[0]
                                            
                                            percentageDamage =((int(totalHealth)-int(remainingHealth)) /int(totalHealth)) *100 
                                            
                                            nickname = nick_names[pokemon]
                                            player = match.group("player")
                                            if("p1" in player): 
                                                healthOne[nickname] = percentageDamage
                                            else : 
                                                healthTwo[nickname] = percentageDamage
     
                                            continue
    
    

         
if __name__ == "__main__":
    r = ReplayDatabase(sys.argv[0])
    names = r.select_all_replays()
    index = 0
    for username in names:
        directory = username
        healthOne = {}
        healthTwo ={}
        nick_names ={}
        team1 = []
        team2 =[]
        team1pokemon = []
        team2pokemon = []
        user1 = ''
        user2 = ''
        statsTeam1  = []
        statsTeam2 =[]
            
        noOfTeam1Pokemon = 0 
        noOfTeam2Pokemon = 0 
            
        noOfFaintedPokemonForTeam1=0 
        noOfFaintedPokemonForTeam2=0
        noofStatsPokemon1 = 0 
        noofStatsPokemon2 = 0 
        turn = 1
        ans = []
        replayid = directory[1]
        for log in directory[2].split("\n"):
            
            index = index+1
            lines = log.split("\n")
            
            handle_line(lines)
            if(ans != [] and ans != None):
                main_ans = ans
                break
        
        if(main_ans != [] and main_ans != None):
            
            if(main_ans[0]!="for"):
                with open("wins.csv", "a") as f1:
                    win_team  = main_ans[1]
                    lose_team = main_ans[2]
                    for i in range(len(win_team)) : 
                        f1.write(str(win_team[i]).strip("[]").replace(" ","")+",0"+","+replayid)
                        f1.write("\n")
                        f1.write(str(lose_team[i]).strip("[]").replace(" ","")+",1"+","+replayid)
                        f1.write("\n")
                        
                    f1.close()
            else: 
                with open("forfeited.csv", "a") as f:
                    win_team  = main_ans[1]
                    lose_team = main_ans[2]
                    for i in range(len(win_team)) : 
                        f.write(str(win_team[i]).strip("[]").replace(" ","")+",0"+","+replayid)
                        f.write("\n")
                        f.write(str(lose_team[i]).strip("[]").replace(" ","")+",1"+","+replayid)
                        f.write("\n")

                        
                    f.close()
            
                    
                    

           

        
   