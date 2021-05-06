from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep
import re

def getGames(year,team):
  team_url = '-'.join(team.lower().split())
  team_url = re.sub('[()]', '', team_url)
  url = 'https://www.sports-reference.com/cfb/schools/'+team_url+'/'+str(year)+'-schedule.html'
  r = requests.get(url)

  if r.status_code == 200:
    soup = BeautifulSoup(r.content, 'html.parser')
    for x in soup.find_all('td', class_='left'):
      if 'opp_name' in str(x):
        opp = x.text
        if opp[1].isdigit(): # have to do this because of teams like Miami (FL)
          opp = opp.split(')\xa0')[1]
        print(opp)
      if 'game_location' in str(x):
        loc = x.text
        if loc == '@':
          loc = 'A'
        if loc == '':
          loc = 'H'
        print(loc)
      if 'date_game' in str(x):
        date = x.text
        print(date)

      # how to format this data to return and save for look up
    return 0
  else:
    return None

if __name__ == '__main__':
  year = 2020

  teamdf = pd.read_csv('teams.csv')
  teams = [x.split(';') for x in teamdf['teams'].values]
  teams = [item for sublist in teams for item in sublist]

  noData = []
  for team in teams:
    print(team)
    games = getGames(year,team)
    if games is None:
      noData.append(team)
    break
    sleep(5)

  print('Teams without data: ',noData)
