## Data Collection
For data collection, we scrapped the user replay data from the top 500 Pokémon showdown gamers (both OU and random battle). We used Selenium and Pandas (Beautiful Soup) to scrape the data from these sites and stored it in an SQLite database. 
The ladder consists of data of the top 500 players of Pokémon showdown for various types of game battles. After getting the top players, we navigated to the replays site to scrap the replay data of all users. The log is in text format. There are keywords( like a switch, move, damage, etc) which represent the gameplay data.

We also scrapped the data from Babiri website to find the top 10 Pokémon used by players. 
This would help us in forming the Pokémon teams if required.


 # Scraping for Babiri Website - babiri_parser.py
 # Scraping for Pokémon Showdown Replays Website - log_scrapper.py
 # Parsing logic for Human Replays Data - log_parser.py
 # Parsing Logic for Winning Prediction - log_parse.py 
 # CSV files used for winning prediction - wins.csv, completed.csv, forfeited.csv
 # database : database_for_scrapping.db 
 
 Basic Scrapping idea taken from https://github.com/vasumv/pokemon_ai/tree/master/log_scraper 
 Scrapped data from top 500 players for ou and genrandom8 battles 
 Scrapped top 100 teams from https://www.babiri.net/#/ 
 
 ## Running the Scrapping Script
 
 To run the script python log_scrapper.py with db_path as arguement
 Eg : python3 log_scraper.py  db_path: database_for_scrapping.db 
 
 
