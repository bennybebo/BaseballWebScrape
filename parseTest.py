import json
import pandas as pd
import requests
import time

playerid_playername_list = {}
playerid_odds_list = {}
with open('data.json') as f:
  jsondata = json.load(f)

  i= 0
  while True:
    try:
      playername = jsondata['markets'][0]['players'][i]['full_name']
      playerid = jsondata['markets'][0]['players'][i]['id']
      playerid_playername_list[playerid] = playername
      #fdmoney = jsondata['markets'][0]['books'][0]['odds'][0]['money']
      #print(playername, playerid)
      i += 1
    except IndexError:
      break

  i= 0
  while True:
    try:
      option_type_id = jsondata['markets'][0]['books'][3]['odds'][i]['option_type_id']
      if option_type_id == 54:
        playerid = jsondata['markets'][0]['books'][3]['odds'][i]['player_id']
        odds = jsondata['markets'][0]['books'][3]['odds'][i]['money']
        playerid_odds_list[playerid] = odds
      i += 1
    except IndexError:
       break
  

combined_list = []
for playerid in playerid_playername_list:
    if playerid in playerid_odds_list:
        playername = playerid_playername_list[playerid]
        odds = playerid_odds_list[playerid]
        combined_list.append((playerid, playername, odds))

'''for entry in combined_list:
    #entry 0 is playerid
    print(entry[1], entry[0], entry[2])'''

pd.set_option('display.max_columns', None)
dataurl = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=onBasePlusSlugging&order=desc&playerPool=ALL'
last15daysurl = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=onBasePlusSlugging&order=desc&playerPool=ALL&timeframe=-14'

r_season = requests.get(url=dataurl).json()
df_season = pd.DataFrame(r_season['stats'])
'''time.sleep(5)
r_15days = requests.get(url = last15daysurl).json()
df_15days = pd.DataFrame(r_15days['stats'])

df_15days.rename(columns={'homeRuns': 'homeRuns_last_15_days'}, inplace=True)

# Merge the two DataFrames based on 'playerID'
merged_df = pd.merge(df_season, df_15days, on='playerId', how='left')
# Fill NaN values in 'homeRuns_last_15_days' with 0
merged_df['homeRuns_last_15_days'].fillna(0, inplace=True)
# Convert 'homeRuns_last_15_days' column to integer
merged_df['homeRuns_last_15_days'] = merged_df['homeRuns_last_15_days'].astype(int)

df = merged_df[merged_df['playerName'].isin(playerid_playername_list.values())]'''

odds_list = []
for index, row in df_season.iterrows():
    playername = row['playerName']
    playerid = None
    for pid, pname in playerid_playername_list.items():
        if pname == playername:
            playerid = pid
            break
    odds = playerid_odds_list.get(playerid)
    odds_list.append(odds)

df_season['odds'] = odds_list

'''#df = (df_season[['playerName', 'teamName', 'homeRuns_last_15_days', 'homeRuns', 'atBatsPerHomeRun', 'odds']])
df = (df_season[['playerName', 'teamName', 'homeRuns', 'atBatsPerHomeRun', 'odds']])
df.to_excel("testicle2.xlsx")'''

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
