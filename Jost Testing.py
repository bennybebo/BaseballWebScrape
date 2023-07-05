'''import json
import pandas as pd
import requests
import time

with open('2data.json') as f:
  jsondata = json.load(f)

away_home_teams = {}

#Loop to gather all home teams playing today and team ids
i= 0
while True:
    try:
      away_team_name = jsondata['games'][i]['teams'][0]['full_name']        
      home_team_name = jsondata['games'][i]['teams'][1]['full_name']   
      away_home_teams[away_team_name] = home_team_name
      #print(home_team_name, away_team_name)
      i += 1
    except IndexError:
      break


import json
import pandas as pd

with open('2data.json') as f:
    jsondata = json.load(f)

away_home_teams = []

# Loop to gather all home teams playing today and team ids
i = 0
while True:
    try:
        away_team_name = jsondata['games'][i]['teams'][0]['full_name']
        home_team_name = jsondata['games'][i]['teams'][1]['full_name']
        away_home_teams.append([away_team_name, 'Away'])
        away_home_teams.append([home_team_name, 'Home'])
        i += 1
    except IndexError:
        break

# Create a DataFrame from the list
df = pd.DataFrame(away_home_teams, columns=['Team', 'Location'])

print(df)'''

import json
import pandas as pd

with open('2data.json') as f:
    jsondata = json.load(f)

away_home_teams = []

# Loop to gather all home teams playing today and team ids
i = 0
while True:
    try:
        away_team_name = jsondata['games'][i]['teams'][0]['full_name']
        home_team_name = jsondata['games'][i]['teams'][1]['full_name']
        away_home_teams.append([away_team_name, home_team_name, 'Away', home_team_name])
        away_home_teams.append([home_team_name, away_team_name, 'Home', home_team_name])
        i += 1
    except IndexError:
        break

# Create a DataFrame from the list
home_team_df = pd.DataFrame(away_home_teams, columns=['Team', 'Opponent', 'Location', 'Home Team'])

print(home_team_df[['Team', 'Home Team']])
