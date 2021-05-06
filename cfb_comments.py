import praw
from config_bot import *
import json
import requests
import redAPI

# Reddit stuff
r = praw.Reddit(user_agent = "ARTCbot 1.3.0 by herumph",
    client_id = ID,
    client_secret = SECRET,
    username = REDDIT_USERNAME,
    password = REDDIT_PASS)

'''headers = {'user_agent': "ARTCbot 1.3.0 by herumph",
    'client_id': ID,
    'client_secret': SECRET,
    'username': REDDIT_USERNAME,
    'password': REDDIT_PASS}'''

def main(subreddit,id):
  submission = r.submission(id=id)
  print('Total comments to load '+str(submission.num_comments))
  # this is super slow, not realistic to run, need another solution
  submission.comments.replace_more(limit=None)
  for comment in submission.comments.list():
    print(comment.body)
  print(len(submission.comments.list()))

if __name__ == '__main__':
  print('Starting parse...')
  main('cfb','j8q4uh')
