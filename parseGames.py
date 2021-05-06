import pandas as pd
from datetime import datetime
import json

# breaking down games into dates that they are played and not games per team
def main(outfile):
    gamedf = pd.read_csv("2020_games.csv")
    print(gamedf)

    dateDict = {}
    seasonEnd = "Dec 19, 2020"
    seasonEnd = datetime.strptime(seasonEnd, "%b %d, %Y")
    for team in gamedf["team"]:
        teamdf = gamedf[(gamedf["team"] == team)]
        # check to make sure the team played games
        if pd.notna(teamdf["opponent"].values[0]):
            opponents = teamdf["opponent"].values[0].split("/")
            locations = teamdf["location"].values[0].split("/")
            dates = teamdf["date"].values[0].split("/")

            for i in range(len(dates)):
                date = dates[i]
                dtDate = datetime.strptime(date, "%b %d, %Y")
                opponent = opponents[i]
                # not counting post season games
                if dtDate < seasonEnd:
                    # add a date if it's not in the dictionary
                    if date not in dateDict.keys():
                        dateDict[date] = []

                    # put each game in the format 'AWAY @ HOME'
                    if locations[i] == "H":
                        format = opponent + " @ " + team
                    elif locations[i] == "A":
                        format = team + " @ " + opponent
                    elif locations[i] == "N":
                        # need a default ordering so we don't double count
                        ordering = sorted([team, opponent])
                        format = ordering[0] + " vs " + ordering[1]

                    # add each game if not added already
                    if format not in dateDict[date]:
                        dateDict[date].append(format)

    print(dateDict)
    with open(outfile, "w") as f:
        json.dump(dateDict, f)


if __name__ == "__main__":
    outfile = "2020_gameDates.json"
    main(outfile)
