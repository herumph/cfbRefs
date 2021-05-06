import time
import requests
import requests.auth
import praw
from config_bot import *


global accessToken
accessToken = None

def getAccessToken():
  client_auth = requests.auth.HTTPBasicAuth(ID, SECRET)
  post_data = {"grant_type": "password", "username": REDDIT_USERNAME, "password": REDDIT_PASS}
  headers = {"User-Agent": userAgent}
  response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
  return response.json()

def makeRequest(apiUrl, useGet=True):
  global accessToken
  if accessToken is None:
    accessToken = getAccessToken()
  headers = {"Authorization": "bearer "  + accessToken['access_token'], "User-Agent": userAgent}
  if useGet:
    response = requests.get(apiUrl, headers=headers)
  else:
    response = requests.post(apiUrl, headers=headers)
  time.sleep(1.1)
  responseJson = response.json()
  if 'error' in responseJson:
    if responseJson['error'] == 401:
      print("Refreshing access token")
      time.sleep(1.1)
      accessToken = getAccessToken()
      headers = {"Authorization": "bearer "  + accessToken['access_token'], "User-Agent": userAgent}
      time.sleep(1.1)
      response = requests.get(apiUrl, headers=headers)
      responseJson = response.json()
  return responseJson


global prawReddit
userAgent = "ARTCbot 1.3.0 by herumph"
prawReddit = praw.Reddit(user_agent = "ARTCbot 1.3.0 by herumph",
    client_id = ID,
    client_secret = SECRET,
    username = REDDIT_USERNAME,
    password = REDDIT_PASS)

# Gets any number of posts
def getPosts(subredditName, numPosts=1000):
  global prawReddit
  subreddit = prawReddit.get_subreddit(subredditName)

  postGetter = praw.helpers.submissions_between(prawReddit, subreddit)

  postArray = []
  numGotten = 0
  while numGotten < numPosts:
    postArray.append(postGetter.next())
    numGotten += 1

  return postArray






# Get all comments from a post
# Submission is a praw submission, obtained via:
# r = redApi.getPraw()
# submission = r.get_submission(submission_id='2zysz7') # (or some other submission id, found via https://www.reddit.com/r/test/comments/2zysz7/ayy/ - the thing after /comments/)
# comments = redApi.getComments(submission)
def getComments(submission):
  requestUrl = 'https://oauth.reddit.com/' + submission.subreddit.url + 'comments/article?&limit=1000&showmore=true&article=' + submission.id
  allData = makeRequest(requestUrl)
  articleData = allData[0]
  comments = allData[1]
  curComments = comments['data']['children']

  resultComments = getCommentsHelper(curComments, submission.name, submission)

  return resultComments




# Print out the tree of comments
def printTree(comments):
  return printTreeHelper(comments, "")


def printTreeHelper(comments, curIndentation):
  resultString = ""
  for comment in comments:
    resultString += curIndentation + comment['data']['body'].replace("\n", "\n" + curIndentation) + "\n"
    if not comment['data']['replies'] == "":
      resultString += printTreeHelper(comment['data']['replies']['data']['children'], curIndentation + "  ")
  return resultString

# Get all comments as a single array
def flattenTree(comments):
  allComments = []
  for comment in comments:
    allComments.append(comment)
    if not comment['data']['replies'] == "":
      allComments += flattenTree(comment['data']['replies']['data']['children'])
  return allComments

# Utility functions for getComments
def expandCommentList(commentList, submission):
  curComments = commentList
  allComments = {}
  while True:
    thingsToExpand = []
    nextComments = []
    allParents = {}
    for comment in curComments:
      if comment['kind'] == "more":
        thingsToExpand += comment['data']['children']
      else:
        if comment['data']['body'][:len("If they are shipping")] == "If they are shipping":
          print(comment)
        allComments[comment['data']['name']] = comment

    if len(thingsToExpand) == 0:
      curComments = []
      break

    curComments = []
    if not len(thingsToExpand) == 0:
      print("total things to expand: " + str(len(thingsToExpand)))
      for i in range(0, int(len(thingsToExpand)/100)+1):
        curCommentIds = thingsToExpand[i*100:min((i+1)*100, len(thingsToExpand))]
        requestUrl = 'https://oauth.reddit.com/api/morechildren.json?api_type=json&link_id=' + submission.name + '&limit=1000&showmore=true&children=' + ",".join(curCommentIds)
        curData = makeRequest(requestUrl)
        if 'json' in curData and 'data' in curData['json']:
          curComments += curData['json']['data']['things']
        print((i+1)*100)

  for comment in curComments:
    allComments[comment['data']['name']] = comment

  return allComments.values()


def lookForMore(comment):
  if comment['kind'] == "more":
    return True
  if not comment['data']['replies'] == "":
    for reply in comment['data']['replies']['data']['children']:
      if lookForMore(reply):
        return True
  return False

def getCommentsHelper(curComments, rootId, submission):
  allComments = expandCommentList(curComments, submission)
  commentMap = {}
  for comment in allComments:
    commentMap[comment['data']['name']] = comment

  allRootComments = []
  for comment in allComments:
    if comment['data']['parent_id'] == rootId:
      allRootComments.append(comment)
    elif comment['data']['parent_id'] in commentMap:
      parentComment = commentMap[comment['data']['parent_id']]
      if parentComment['data']['replies'] == "":
        parentComment['data']['replies'] = {'data': {'children': []}}
      alreadyChild = False
      for childComment in parentComment['data']['replies']['data']['children']:
        if childComment['data']['name'] == comment['data']['name']:
          alreadyChild = True
          break
      if not alreadyChild:
        parentComment['data']['replies']['data']['children'].append(comment)
    else:
      print("pls halp")

  completedComments = []
  needMoreComments = []

  for comment in allRootComments:
    if not comment['data']['replies'] == "" or comment['kind'] == 'more':
      hasMore = lookForMore(comment)

      if hasMore:
        needMoreComments.append(comment)
      else:
        replyComments = getCommentsHelper(comment['data']['replies']['data']['children'], comment['data']['name'], submission)
        comment['data']['replies']['data']['children'] = replyComments
        completedComments.append(comment)
    else:
      completedComments.append(comment)
  for comment in needMoreComments:
    requestUrl = 'https://oauth.reddit.com/' + submission.subreddit.url + 'comments/article?&limit=1000&showmore=true&article=' + submission.id + "&comment=" + comment['data']['id']
    allData = makeRequest(requestUrl)
    articleData = allData[0]
    comment = allData[1]['data']['children'][0]
    if comment['data']['replies'] == "":
      completedComments.append(comment)
    else:
      comments = comment['data']['replies']['data']['children']
      actualComments = getCommentsHelper(comments, comment['data']['name'], submission)
      comment['data']['replies']['data']['children'] = actualComments
      completedComments.append(comment)

  return completedComments
