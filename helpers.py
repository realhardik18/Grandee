import tweepy
from creds import BEARER_TOKEN,API_KEY,API_KEY_SECRET,ACCSES_TOKEN,ACCSESS_TOKEN_SECRET

client=tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCSES_TOKEN, access_token_secret=ACCSESS_TOKEN_SECRET)

class Twitter:
    def __init__(self,user_link):
        self.user_link=user_link
    def GetUsernameFromLink(user_link):
        #https://twitter.com/realhardik18
        return user_link[user_link.index('.com/')+5:]

print(Twitter.GetUsernameFromLink('https://twitter.com/Ultimateadi18'))
