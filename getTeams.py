from bs4 import BeautifulSoup
import requests

conferences = ['acc','american','big-12','big-ten','cusa','mac','mwc','pac-12','sec','sun-belt']

confDict = {x: [] for x in conferences}
for conf in conferences:
  url = 'https://www.sports-reference.com/cfb/conferences/'+conf+'/2020.html'
  r = requests.get(url)
  if r.status_code == 200:
    soup = BeautifulSoup(r.content, 'html.parser')
    for x in soup.find_all('th', class_="left"):
      if 'school_name' in str(x) and 'a href' in str(x):
        confDict[conf].append(x.text)
  confDict[conf] = list(set(confDict[conf]))

print(confDict)
with open('teams.csv','w') as f:
  f.write('conference,teams\n')
  for key in confDict.keys():
    f.write(key+','+';'.join(confDict[key])+'\n')
