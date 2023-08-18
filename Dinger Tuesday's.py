import json
import http.client
import pandas as pd
import requests
import re
import time
import numpy as np
import xlwings as xw
from datetime import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from bs4 import BeautifulSoup

current_date = datetime.now().strftime("%Y%m%d") # Get current date in proper format
conn = http.client.HTTPSConnection("api.actionnetwork.com") # Establish connection to website
payload = ""
headers = { 'authority': "api.actionnetwork.com" }

def get_json_data(endpoint):
   conn.request("GET", endpoint + current_date, payload, headers)
   res = conn.getresponse() # Get result of request
   data = res.read() # Read result
   json_data = data.decode("utf-8") # Decode result data
   return json.loads(json_data)

dt_now = datetime.now()
start = time.time()
# Scraping player HR odds from fanDuel
props_json = get_json_data("/web/v1/leagues/8/props/core_bet_type_33_hr?bookIds=69%2C75%2C68%2C123%2C71%2C32%2C76%2C79&date=")

playerid_playername_list = {} # Dictionary to map playerId to playerName
playerid_odds_list = {} # Dictionary to map playedId to odds
i= 0
while True: # Get playerName and playerId and store in dictionary
  try:
    playername = props_json['markets'][0]['players'][i]['full_name']
    playerid = props_json['markets'][0]['players'][i]['id']
    playerid_playername_list[playerid] = playername
    i += 1
  except IndexError:
    break

i= 0
while True: # Get playerId and odds and store in dictionary
  try:
    option_type_id = props_json['markets'][0]['books'][3]['odds'][i]['option_type_id'] 
    if option_type_id == 54:          #Option type 54 means a plus odds bet e.g. +100
      playerid = props_json['markets'][0]['books'][3]['odds'][i]['player_id']
      odds = props_json['markets'][0]['books'][3]['odds'][i]['money']
      playerid_odds_list[playerid] = odds
    i += 1
  except IndexError:
    break

playerid_playername_odds_list = [] # List that stores playerId, playerName, odds
for playerid in playerid_playername_list:
    if playerid in playerid_odds_list: # If player can be bet on, add their odds
        playername = playerid_playername_list[playerid]
        odds = playerid_odds_list[playerid]
        playerid_playername_odds_list.append((playerid, playername, odds))

# MLB stats for a player from the entire season url
season_data_url = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=onBasePlusSlugging&order=desc&playerPool=ALL'
# MLB stats for a  player from the last 15 days url
last_15_days_data_url = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=onBasePlusSlugging&order=desc&playerPool=ALL&daysBack=-14'

# Scraping MLB player stats
r_season = requests.get(url= season_data_url).json()
df_season_stats = pd.DataFrame(r_season['stats'])
time.sleep(1)     #Wait in between
r_15days = requests.get(url = last_15_days_data_url).json()
df_15days_stats = pd.DataFrame(r_15days['stats'])

# Create a dictionary mapping player IDs to their respective homeRuns_last_15_days values
homeRuns_last_15_days_dict = df_15days_stats.set_index('playerId')['homeRuns'].to_dict()
# Add a new column 'homeRuns_last_15_days' to df_season using the mapping dictionary
df_season_stats['homeRuns_last_15_days'] = df_season_stats['playerId'].map(homeRuns_last_15_days_dict)
# Fill NaN values in 'homeRuns_last_15_days' with 0
df_season_stats['homeRuns_last_15_days'].fillna(0, inplace=True)
# Convert 'homeRuns_last_15_days' column to integer
df_season_stats['homeRuns_last_15_days'] = df_season_stats['homeRuns_last_15_days'].astype(int)
# Remove all players that do not have available bets
df_combined_stats = df_season_stats[df_season_stats['playerName'].isin(playerid_playername_list.values())]

odds_list = []
for index, row in df_combined_stats.iterrows():
    playername = row['playerName']
    playerid = None
    for pid, pname in playerid_playername_list.items():
      if pname == playername:
        playerid = pid
        break
    odds = playerid_odds_list.get(playerid)
    odds_list.append(odds)

df_new = df_combined_stats.copy()
df_new['Odds'] = odds_list.copy()
df_new = df_new[['playerName', 'teamName', 'homeRuns_last_15_days', 'homeRuns', 'atBatsPerHomeRun', 'Odds']]

# Scraping home team data
home_teams_json = get_json_data("/web/v1/scoreboard/mlb?period=game&bookIds=15%2C30%2C76%2C75%2C123%2C69%2C68%2C972%2C71%2C247%2C79&date=")

away_home_teams = [] # Dictionary that maps away team to home team
i = 0
while True: # Loop to gather all home teams playing today and team ids
    try:
        home_team_name = home_teams_json['games'][i]['teams'][0]['full_name']
        away_team_name = home_teams_json['games'][i]['teams'][1]['full_name']
        away_home_teams.append([away_team_name, home_team_name, 'Away', home_team_name])
        away_home_teams.append([home_team_name, away_team_name, 'Home', home_team_name])
        i += 1
    except IndexError:
        break

# Create a DataFrame from the list
home_team_df2 = pd.DataFrame(away_home_teams, columns=['Team', 'Opponent', 'Location', 'Home Team'])
home_team_df = home_team_df2[['Team', 'Home Team']]

# Scraping home run totals for each stadium
url = 'https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year=2023&batSide=&stat=index_wOBA&condition=All&rolling=no'
response = requests.get(url) # Send a GET request to the webpage

soup = BeautifulSoup(response.text, 'html.parser')
stats_table = soup.find('div', {'class': 'article-template'})
raw_data = stats_table.find_all('script')

pattern = re.compile(r'var data = (\[.*?\]);')
matches = pattern.search(str(raw_data))
if matches:
    json_data = matches.group(1)
    var_data = json.loads(json_data)

    # Create a DataFrame and rename columns
    df = pd.DataFrame(var_data).rename(columns={'name_display_club': 'Team', 'index_hr': 'HR'})

    # Select only the 'Team' and 'HR' columns
    df_selected = df[['Team', 'HR']]
else:
    print('No JSON data found.')

df_selected['Team'] = df_selected['Team'].replace('D-backs', 'Diamondbacks')
home_team_df['Matched Team'] = home_team_df['Home Team'].apply(lambda x: process.extractOne(x, df_selected['Team'], scorer=fuzz.token_set_ratio)[0])
merged_df = pd.merge(home_team_df, df_selected[['Team', 'HR']], how='left', left_on='Matched Team', right_on='Team')
merged_df = merged_df[['Team_x', 'Home Team', 'HR']]
merged_df.rename(columns={'Team_x': 'Team'}, inplace=True)

# Remove duplicates from merged_df based on the 'Team' column
merged_df = merged_df.drop_duplicates(subset='Team')

new_df = df_new.copy()  # Create a copy of the DataFrame
new_df['HR'] = df_new['teamName'].map(merged_df.set_index('Team')['HR'])  # Add the 'HR' column
new_df['HR'].fillna(0, inplace=True)
new_df['HR'] = new_df['HR'].astype(int)
new_df['atBatsPerHomeRun'] = new_df['atBatsPerHomeRun'].replace('-.--', np.nan)
new_df['atBatsPerHomeRun'] = new_df['atBatsPerHomeRun'].astype(float)
new_df = new_df.dropna(subset=['Odds'])  # Drop rows with NaN values in the 'odds' column
new_df = new_df.rename(columns={'playerName': 'Player', 'teamName': 'Team', 'homeRuns_last_15_days': 'HR Last 15 Days',
                      'homeRuns': 'Season HR Total', 'atBatsPerHomeRun': 'AB/HR', 'HR': 'HR in Stadium YTD'})
new_df = new_df.sort_values(by=['HR Last 15 Days', 'Season HR Total'], ascending=False)
new_df = new_df.head(35)

new_df['Odds'] = new_df['Odds'].astype(int)
# Move 'Odds' column to the far right
new_df = new_df[[col for col in new_df.columns if col != 'Odds'] + ['Odds']]
# Add '+' sign to each odds value
new_df['Odds'] = '+' + new_df['Odds'].astype(str)

excel_file_path =  r'C:\Users\thisi\OneDrive\Desktop\baseball web scrap\Dinger Tuesday Template.xlsm'

app = xw.App(visible=True)
workbook = app.books.open(excel_file_path)

try:
    # Specify the sheet name where you want to paste the DataFrame
    sheet_name = 'New Data'

    # Activate the sheet
    sheet = workbook.sheets[sheet_name]
    sheet.activate()

    # Delete everything on the sheet
    sheet.clear()

    # Write the DataFrame to the sheet starting from cell A1
    sheet.range('A1').value = new_df

    # Run the macro
    macro_name = 'Format_Data4'
    module_name = 'Module2'
    macro_code = workbook.macro(module_name + '.' + macro_name)
    macro_code()

    time.sleep(2)

finally:
    workbook.save()
    workbook.close()

    app.quit()

print('Check your desktop for the HR Sheet Pic')
print("The",dt_now.month,'/',dt_now.day,'/',dt_now.year,"HR Sheet took",round(time.time()-start),"seconds to run.")