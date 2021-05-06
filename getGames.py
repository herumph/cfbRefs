from bs4 import BeautifulSoup
import requests
import pandas as pd
from time import sleep
import re


def getGames(year, team):
    team_url = "-".join(team.lower().split())
    team_url = re.sub("[()]", "", team_url)
    url = (
        "https://www.sports-reference.com/cfb/schools/"
        + team_url
        + "/"
        + str(year)
        + "-schedule.html"
    )
    r = requests.get(url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        teamDict = {"team": team, "opponent": [], "date": [], "location": []}

        for x in soup.find_all("td", class_="left"):
            if "opp_name" in str(x):
                opp = x.text
                if opp[1].isdigit():  # have to do this because of teams like Miami (FL)
                    opp = opp.split(")\xa0")[1]
                teamDict["opponent"].append(opp)
            if "game_location" in str(x):
                loc = x.text
                if loc == "@":
                    loc = "A"
                if loc == "":
                    loc = "H"
                teamDict["location"].append(loc)
            if "date_game" in str(x):
                date = x.text
                teamDict["date"].append(date)

        return teamDict
    else:
        return None


if __name__ == "__main__":
    year = 2020

    teamdf = pd.read_csv("teams.csv")
    teams = [x.split(";") for x in teamdf["teams"].values]
    teams = [item for sublist in teams for item in sublist]

    # teams that 404 because of naming differences
    missedTeams = {
        "Pitt": "pittsburgh",
        "SMU": "southern-methodist",
        "UCF": "central-florida",
        "UTSA": "texas-san-antonio",
        "UAB": "alabama-birmingham",
        "UTEP": "texas-el-paso",
        "USC": "southern-california",
        "Texas A&M": "texas-am",
        "LSU": "louisiana-state",
        "Ole Miss": "mississippi",
        "Louisiana": "louisiana-lafayette",
    }

    noData = []
    df = pd.DataFrame()
    for team in teams:
        print(team)
        if team not in missedTeams.keys():
            teamDict = getGames(year, team)
        else:
            teamDict = getGames(year, missedTeams[team])
            teamDict["team"] = team
        print(teamDict)
        if teamDict is None:
            noData.append(team)
        else:
            joinKeys = ["opponent", "date", "location"]
            for key in joinKeys:
                teamDict[key] = "/".join(teamDict[key])
            df = df.append(teamDict, ignore_index=True)
        sleep(2)  # to not spam the website too much
    df.to_csv(str(year) + "_games.csv")

    print("Teams without data: ", noData)
