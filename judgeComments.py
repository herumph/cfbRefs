import pandas as pd
import pyinputplus as pyip
import re

trainingGames = [
    "clemson_tosu2019",
    "tennessee_scar2019",
    "auburn_lsu2019",
    "notredame_michigan2019",
]

for game in trainingGames:
    print("Now judging:", " v ".join(game.split("_"))[:-4])
    commentdf = pd.read_csv(game + ".csv")

    # the dataframe loaded here (commentdf) only has one column (think dictionary key) "body"
    # so what we want to do is loop over each row in the dataframe and get the comment body
    # this loop is basically the same as enumerating a dictionary
    commentType = []
    for ind, row in commentdf.iterrows():
        # the following variable is just a string of each reddit comment
        # so this is where you'll look at the string and see what's "in" it :)
        a = row["body"]
        match = re.search("ref|call|flag|penalty|review|targeting|holding|offsides|horse collar|facemask|fumble|wasn\'t down|out of bounds|ruled|rule|ruling|roughing|passer|ejected|replay|refs|interference|blind|bullshit|screwed|called|fucked|biased|illegal|late|calling", a, re.IGNORECASE)
        if match:
            print(row) 
            judgment = pyip.inputInt("""Is the comment:
            1. Not about the refs
            2. Expressing positive sentiment toward the refs
            3. Expressing negative sentiment toward the refs""", min=1, max=3)
            commentType.append(judgment)
        else:
            commentType.append(0)

        # after you get what type of comment it is, e.g. not about the refs, good refs, bads ref
        # append the type to commentType (type can be whatever you want, string/int/whatever)

    # now that each comment was judged we add a new column to the dataframe with the judgement
    # and save the edited dataframe
    commentdf["type"] = commentType
    commentdf.to_csv(game + "_judged.csv")

    print(commentdf)
