from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

r = requests.get('https://ballparkpal.com/GameSimulations.php', headers=headers)
html_data = r.text

soup = BeautifulSoup(html_data, 'html.parser')
# Find all <div style="width: 100vw;"> elements
divs_with_width = soup.find_all('div', style='width: 100vw;')

# Iterate over each div with width style
for div in divs_with_width:
    inner_divs = div.find_all('div')
    if len(inner_divs) >= 6:
        away_team = inner_divs[7].text.strip()
        home_team = inner_divs[11].text.strip()
        yrfi = inner_divs[58].text.strip()
        print(f"Away Team: {away_team}")
        print(f"Home Team: {home_team}")
        print(yrfi)
        print("-------------------------------")
