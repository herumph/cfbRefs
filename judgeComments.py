import pandas as pd

trainingGames = ['clemson_tosu2019', 'tennessee_scar2019', 'auburn_lsu2019', 'notredame_michigan2019']

for game in trainingGames:
  print('Now judging:',' v '.join(game.split('_'))[:-4])
  commentdf = pd.read_csv(game+'.csv')

  # the dataframe loaded here (commentdf) only has one column (think dictionary key) "body"
  # so what we want to do is loop over each row in the dataframe and get the comment body
  # this loop is basically the same as enumerating a dictionary
  commentType = []
  for ind,row in commentdf.iterrows():
    # the following variable is just a string of each reddit comment
    # so this is where you'll look at the string and see what's "in" it :)
    a = row['body']

    # after you get what type of comment it is, e.g. not about the refs, good refs, bads ref
    # append the type to commentType (type can be whatever you want, string/int/whatever)
    commentType.append(0)

  # now that each comment was judged we add a new column to the dataframe with the judgement
  # and save the edited dataframe
  commentdf['type'] = commentType
  commentdf.to_csv(game+'_judged.csv')

  print(commentdf)
