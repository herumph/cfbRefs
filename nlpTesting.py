import pandas as pd
import spacy
import re
import json
from textblob.classifiers import NaiveBayesClassifier
from textblob import TextBlob

nlp = spacy.load("en_core_web_sm")

trainingGames = [
    "clemson_tosu2019",
    "tennessee_scar2019",
    "auburn_lsu2019",
    "notredame_michigan2019",
]

with open("keywords.json", "r") as f:
    keywords = json.load(f)
keywords = "|".join(keywords["keywords"])

with open("testTraining.json", "r") as f:
    training = json.load(f)

mlTraining = []
for sentence in training['sentences']:
    mlTraining.append(tuple(sentence))
print(mlTraining)

trainingdf = pd.read_csv('tennessee_scar2019_judged.csv')
trainingdf = trainingdf[(trainingdf['type']==2)|(trainingdf['type']==3)]
print(len(trainingdf[(trainingdf['type']==2)]))

#mlTraining = []
for ind,row in trainingdf.iterrows():
    if row['type'] == 2:
        mlTraining.append((row['body'],'positive'))
    elif row['type'] == 3:
        mlTraining.append((row['body'],'negative'))

cl = NaiveBayesClassifier(mlTraining)

i = 0
for game in trainingGames:
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
            blob = TextBlob(commentBody, classifier=cl)
            print(commentBody,blob.classify())
            print(blob.sentiment)
            print('---------------------------')
            i = i + 1
        if i>50:
            break
    break
    #print(commentdf)
