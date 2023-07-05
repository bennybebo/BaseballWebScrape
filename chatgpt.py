import json
import pandas as pd
import requests

playerid_playername_list = {}
playerid_odds_list = {}
with open('data.json') as f:
    jsondata = json.load(f)

    i = 0
    while True:
        try:
            playername = jsondata['markets'][0]['players'][i]['full_name']
            playerid = jsondata['markets'][0]['players'][i]['id']
            playerid_playername_list[playerid] = playername
            i += 1
        except IndexError:
            break

    i = 0
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

pd.set_option('display.max_columns', None)
dataurl = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=onBasePlusSlugging&order=desc&playerPool=ALL'
last15daysurl = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=onBasePlusSlugging&order=desc&playerPool=ALL&timeframe=-14'

r_season = requests.get(url=dataurl).json()
df_season = pd.DataFrame(r_season['stats'])

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

cool_df = df_season[['playerName', 'teamName', 'homeRuns', 'atBatsPerHomeRun', 'odds']]
cool_df = cool_df.merge(home_team_df[['Team', 'Home Team']], left_on='teamName', right_on='Team', how='left')

# Drop the 'Team' column
cool_df.drop('Team', axis=1, inplace=True)

print(cool_df)



