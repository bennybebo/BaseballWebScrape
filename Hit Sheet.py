import requests
import pandas as pd
from datetime import datetime
import http.client
import json
import time
import xlwings as xw
import threading

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
###################################################################################
# Get list of all players you can bet on
props_json = get_json_data("/web/v1/leagues/8/props/core_bet_type_36_hits?bookIds=69,75,68,123,71,32,76,79%2C75%2C68%2C123%2C71%2C32%2C76%2C79&date=")

playerid_playername_list = {}  # Dictionary to map playerId to playerName

i = 0
while True:  # Get playerName and playerId and store in dictionary
    try:
        playername = props_json['markets'][0]['players'][i]['full_name']
        playerid = props_json['markets'][0]['players'][i]['id']
        playerid_playername_list[playerid] = playername
        i += 1
    except IndexError:
        break

# Create DataFrame with all players and player IDs
endpoint_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
response = requests.get(endpoint_url)
data = response.json()

player_data = []
if 'teams' in data and len(data['teams']) > 0:
    for team in data['teams']:
        team_id = team['id']
        team_name = team['name']

        roster_endpoint_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/fullSeason"

        response = requests.get(roster_endpoint_url)
        data = response.json()

        if 'roster' in data and len(data['roster']) > 0:
            for player in data['roster']:
                player_id = player['person']['id']
                player_name = player['person']['fullName']

                player_data.append({'Player ID': player_id, 'Player Name': player_name, 'Team': team_name})

df_players = pd.DataFrame(player_data)

# Exclude players not in playerid_playername_list
df_players_filtered = df_players[df_players['Player Name'].isin(playerid_playername_list.values())]
print('Got list of all players you can bet on.')
#########################################################################################################
# Function to calculate hit percentage for a player
def calculate_hit_percentages(player_id):
    endpoint_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&group=hitting&season=2023&gameType=R"
    response = requests.get(endpoint_url)
    data = response.json()

    hit_percentage_last_10 = 0
    hit_percentage_season = 0

    if 'stats' in data and len(data['stats']) > 0:
        game_log = data['stats'][0]['splits']
        num_games = len(game_log)

        if num_games >= 10:
            last_ten_games = game_log[-10:]
            num_games_with_hits_last_10 = sum(game['stat']['hits'] > 0 for game in last_ten_games)
            hit_percentage_last_10 = (num_games_with_hits_last_10 / len(last_ten_games)) * 100

        num_games_with_hits_season = sum(game['stat']['hits'] > 0 for game in game_log)
        hit_percentage_season = (num_games_with_hits_season / num_games) * 100

        return hit_percentage_last_10, hit_percentage_season

    return None, None

def asynchronous_task(player_id, result_dict):
    hit_percentages = calculate_hit_percentages(player_id)
    result_dict[player_id] = hit_percentages
    
player_ids = df_players_filtered['Player ID'].tolist()
results = {}  # Dictionary to store results

threads = []
for player_id in player_ids:
    thread = threading.Thread(target=asynchronous_task, args=(player_id, results))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Create a new DataFrame with hit percentages
hit_percentages_df = pd.DataFrame.from_dict(results, orient='index', columns=['L10 Hit Rate', 'Season Hit Rate'])
hit_percentages_df.index.name = 'Player ID'

# Merge hit_percentages_df with df_players_filtered
df_players_final = df_players_filtered.merge(hit_percentages_df, left_on='Player ID', right_index=True)

# Sort the DataFrame by 'L10 Hit Rate' from high to low and then by 'Season Hit Rate' from high to low
df_players_final = df_players_final.sort_values(['L10 Hit Rate', 'Season Hit Rate'], ascending=[False, False])
print('Calculated hit rate last ten games and hit rate for the season.')
############################################################################################################################################################################
home_teams_json = get_json_data("/web/v1/scoreboard/mlb?period=game&bookIds=15%2C30%2C76%2C75%2C123%2C69%2C68%2C972%2C71%2C247%2C79&date=")

away_home_teams = [] # Dictionary that maps away team to home team
i = 0
while True: # Loop to gather all home teams playing today and team ids
    try:
        away_team_name = home_teams_json['games'][i]['teams'][0]['full_name']
        home_team_name = home_teams_json['games'][i]['teams'][1]['full_name']
        away_home_teams.append([away_team_name, home_team_name, 'Away', home_team_name])
        away_home_teams.append([home_team_name, away_team_name, 'Home', home_team_name])
        i += 1
    except IndexError:
        break

# Create a DataFrame from the list
home_team_df2 = pd.DataFrame(away_home_teams, columns=['Team', 'Opponent', 'Location', 'Home Team'])
home_team_df = home_team_df2[['Team', 'Home Team']]
print('Got the scedhule of all the games today.')
############################################################################################################################################################################
props_json = get_json_data("/web/v1/leagues/8/projections/core_bet_type_37_strikeouts?bookIds=69,75,68,123,71,32,76,79&date=")

playerid_playername_list = {} # Dictionary to map playerId to playerName
i= 0
while True: # Get playerName and playerId and store in dictionary
  try:
    playername = props_json['players'][i]['full_name']
    playerid = props_json['players'][i]['id']
    playerid_playername_list[playerid] = playername
    i += 1
  except IndexError:
    break

playerthrow_list = {} # Dictionary to map playedId to odds  
i= 0
while True: # Get playerId and odds and store in dictionary
  try:
    playerid = props_json['players'][i]['id']
    pitcherhand = props_json['players'][i]['handedness']['throw']
    playerthrow_list[playerid] = pitcherhand
    i += 1
  except IndexError:
    break

playerid_teamid_list = {}  
i= 0
while True: # Get playerId and odds and store in dictionary
  try:
    playerid2 = props_json['playerProps'][i]['player_id']
    teamid = props_json['playerProps'][i]['team_id']
    playerid_teamid_list[playerid2] = teamid
    i += 1
  except IndexError:
    break

playerid_playername_hand_list = [] # List that stores playerId, playerName, odds
for playerid in playerid_playername_list:
    if playerid in playerthrow_list: # If player can be bet on, add their odds
        playername = playerid_playername_list[playerid]
        hand = playerthrow_list[playerid]
        playerid_playername_hand_list.append((playerid, playername, hand))

playerid_playername_hand_teamid_list = [] # List that stores playerId, playerName, odds
for playerid in playerid_playername_list:
    if playerid in playerthrow_list: # If player can be bet on, add their odds
        playername = playerid_playername_list[playerid]
        hand = playerthrow_list[playerid]
        teamid = playerid_teamid_list[playerid]
        playerid_playername_hand_teamid_list.append((playerid, playername, hand, teamid))      

# Create a new DataFrame to store updated playerid_playername_hand_teamid_list
df_updated = pd.DataFrame(playerid_playername_hand_teamid_list, columns=['playerId', 'playerName', 'hand', 'teamId'])
print('Got the list of all the pitchers starting today.')
############################################################################################################################################################################
props_json = get_json_data("/web/v1/scoreboard/mlb?period=game&date=")

away_teamId = props_json['games'][0]['teams'][0]['id']
away_teamName = props_json['games'][0]['teams'][0]['full_name']
home_teamId = props_json['games'][0]['teams'][1]['id']
home_teamName = props_json['games'][0]['teams'][1]['full_name']

awayTeam_list = {} # Dictionary to map away_teamId to away_teamName
i = 0
while True: # Get away_teamId and away_teamName and store in dictionary
  try:
    away_teamId = props_json['games'][i]['teams'][0]['id']
    away_teamName = props_json['games'][i]['teams'][0]['full_name']
    awayTeam_list[away_teamId] = away_teamName
    i += 1
  except IndexError:
    break

homeTeam_list = {} # Dictionary to map home_teamId to home_teamName
i = 0
while True: # Get home_teamId and home_teamName and store in dictionary
  try:
    home_teamId = props_json['games'][i]['teams'][1]['id']
    home_teamName = props_json['games'][i]['teams'][1]['full_name']
    homeTeam_list[home_teamId] = home_teamName
    i += 1
  except IndexError:
    break

# Create a list of dictionaries containing teamId and teamName
team_data = [{'teamId': teamId, 'teamName': teamName} for teamId, teamName in awayTeam_list.items()] + [{'teamId': teamId, 'teamName': teamName} for teamId, teamName in homeTeam_list.items()]

# Create a DataFrame from the list of dictionaries
team_df = pd.DataFrame(team_data)

# Merge df_updated with team_df to update teamId to teamName
df_updated = df_updated.merge(team_df, on='teamId', how='left')
df_updated.drop('teamId', axis=1, inplace=True) # Remove the original teamId column

combined_df = home_team_df2.merge(df_updated, left_on='Opponent', right_on='teamName', how='inner')
combined_df.drop('playerId', axis=1, inplace=True)  # Drop the 'playerId' column
combined_df.rename(columns={'playerName': 'Pitcher'}, inplace=True)  # Rename 'playerName' to 'Pitcher'

opp_pitchHand_df = combined_df[['Team', 'hand']].copy()

# Merge df_players_filtered and opp_pitchHand_df based on the 'Team' column
merged_df69 = df_players_final.merge(opp_pitchHand_df, on='Team', how='left')
merged_df69.dropna(subset=['hand'], inplace=True)
############################################################################################################################################################################
# vs left handers
l_season_data_url = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=battingAverage&order=desc&playerPool=ALL&sitCodes=vl'
l_season = requests.get(url= l_season_data_url).json()
df_season_stats = pd.DataFrame(l_season['stats'])

vs_left_list = {} # Dictionary to map playerId to playerName
i= 0
while True: # Get playerName and playerId and store in dictionary
  try:
    playername = l_season['stats'][i]['playerName']
    r_avg = l_season['stats'][i]['avg']
    vs_left_list[playername] = r_avg
    i += 1
  except IndexError:
    break 

# vs right handers
r_season_data_url = 'https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=2023&sportId=1&stats=season&group=hitting&gameType=R&limit=700&offset=0&sortStat=battingAverage&order=desc&playerPool=ALL&sitCodes=vr'
r_season = requests.get(url= r_season_data_url).json()
df_season_stats = pd.DataFrame(r_season['stats'])

vs_right_list = {} # Dictionary to map playedId to odds
i= 0
while True: # Get playerName and playerId and store in dictionary
  try:
    playername = r_season['stats'][i]['playerName']
    r_avg = r_season['stats'][i]['avg']
    vs_right_list[playername] = r_avg
    i += 1
  except IndexError:
    break

combined_list7 = []

for playerName in vs_left_list:
    if playerName in vs_right_list:
        avg_vs_left = vs_left_list[playerName]
        avg_vs_right = vs_right_list[playerName]
        combined_list7.append([playerName, avg_vs_left, avg_vs_right])

batter_vs_hand_df = pd.DataFrame(combined_list7, columns=['Player Name', 'Avg vs Left', 'Avg vs Right'])
print('Got batting averages for all batters vs lefties and righties')
############################################################################################################################################################################
merged_df8 = merged_df69.merge(batter_vs_hand_df, left_on='Player Name', right_on='Player Name', how='left')

# Create a new column 'avg_vs_hand' in merged_df
merged_df8['avg_vs_hand'] = merged_df8.apply(lambda row: row['Avg vs Left'] if row['hand'] == 'L' else row['Avg vs Right'], axis=1)
# Select the desired columns in the final dataframe
final_df = merged_df8[['Player Name', 'Team', 'L10 Hit Rate', 'Season Hit Rate', 'avg_vs_hand']].copy()

# Rename the columns in the copied dataframe
final_df.rename(columns={'Player Name': 'Player', 'avg_vs_hand': 'Avg vs Handed Pitcher'}, inplace=True)
final_df.reset_index(drop=True, inplace=True)
final_df = final_df.drop_duplicates(subset=['Player'])
final_df = final_df.head(25)
print('Put everything together into final_df')
############################################################################################################################################################################
excel_file_path = r'C:\Users\thisi\OneDrive\Desktop\baseball web scrap\One Hit Template.xlsm'

app = xw.App(visible=True)

workbook = app.books.open(excel_file_path)

try:
    sheet_name = 'New Data'  # Specify the sheet name where you want to paste the DataFrame
    sheet = workbook.sheets[sheet_name] # Activate the sheet
    sheet.activate()
    sheet.clear()  # Delete everything on the sheet
    sheet.range('A1').value = final_df  # Write the DataFrame to the sheet starting from cell A1

    # Run the macro
    macro_name = 'Format_Data4'
    module_name = 'Module2'
    macro_code = workbook.macro(module_name + '.' + macro_name)
    macro_code()

    time.sleep(1)

finally:
    # Save and close the workbook and quit the Excel application
    workbook.save()
    workbook.close()
    app.quit()

print("The",dt_now.month,'/',dt_now.day,'/',dt_now.year,"Hit Sheet took",round(time.time()-start),"seconds to run.")