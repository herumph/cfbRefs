import pandas as pd
import pyinputplus as pyip
import re
import json

pd.set_option("display.max_colwidth", None)


def main(game, keywords):
    print("Now judging:", " v ".join(game.split("_"))[:-4])
    commentdf = pd.read_csv(game + ".csv")
    commentType = []

    for ind, row in commentdf.iterrows():
        commentBody = row["body"]
        match = re.search(
            keywords,
            commentBody,
            re.IGNORECASE,
        )
        if match:
            print(row)
            judgment = pyip.inputInt(
                """Is the comment:
            1. Not about the refs
            2. Expressing positive sentiment toward the refs
            3. Expressing negative sentiment toward the refs\n""",
                min=1,
                max=3,
            )
            commentType.append(judgment)
        else:
            commentType.append(0)

    commentdf["type"] = commentType
    commentdf.to_csv(game + "_judged.csv")

    return commentdf


if __name__ == "__main__":
    trainingGames = [
        "clemson_tosu2019",
        "tennessee_scar2019",
        "auburn_lsu2019",
        "notredame_michigan2019",
    ]

    with open("keywords.json", "r") as f:
        keywords = json.load(f)
    keywords = "|".join(keywords["keywords"])

    for game in trainingGames:
        main(game, keywords)
