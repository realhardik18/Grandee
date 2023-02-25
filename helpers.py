import tweepy
from googleapiclient.discovery import build
from creds import TWITTER_BEARER_TOKEN,TWITTER_API_KEY,TWITTER_API_KEY_SECRET,TWITTER_ACCSES_TOKEN,TWITTER_ACCSESS_TOKEN_SECRET,YOUTUBE_API_KEY

client=tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN, consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_KEY_SECRET, access_token=TWITTER_ACCSES_TOKEN, access_token_secret=TWITTER_ACCSESS_TOKEN_SECRET)

class Twitter:
    def __init__(self,user_link):
        self.user_link=user_link
    def GetUsernameFromLink(user_link):
        #https://twitter.com/realhardik18
        return user_link[user_link.index('.com/')+5:]
    def GetUserID(user_link):
        return client.get_user(username=Twitter.GetUsernameFromLink(user_link=user_link)).data['id']
    def GetUserFollowers(user_link):
        return client.get_user(username=Twitter.GetUsernameFromLink(user_link=user_link),user_fields=['public_metrics']).data['public_metrics']['followers_count']
    def GetUserFollowing(user_link):
        return client.get_user(username=Twitter.GetUsernameFromLink(user_link=user_link),user_fields=['public_metrics']).data['public_metrics']['following_count']
    def GetUserTweetCount(user_link):
        return client.get_user(username=Twitter.GetUsernameFromLink(user_link=user_link),user_fields=['public_metrics']).data['public_metrics']['tweet_count']
    def GetRecentTweet(user_link):
        tweet = client.get_users_tweets(Twitter.GetUserID(user_link=user_link)).data[0]
        metrics=client.get_tweet(tweet.id,tweet_fields=['public_metrics']).data['public_metrics']
        data={
            'id':tweet.id,
            'content':tweet.text,
            "likes":metrics['like_count'],
            "views":metrics['impression_count']
        }
        return data
        
class Youtube:
    def __init__(self,id):
        self.id=id
    def GetChannelStats(id):
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.channels().list(part='statistics',id=id)
        response = request.execute()
        data={
            "subs":response['items'][0]['statistics']['subscriberCount'],
            "views":response['items'][0]['statistics']['viewCount'],
            "videos":response['items'][0]['statistics']['videoCount']
        }
        return data
    

#print(Twitter.GetUsernameFromLink('https://twitter.com/Ultimateadi18'))
#print(Twitter.GetUserFollowers(user_link='https://twitter.com/Ultimateadi18'))
#print(Twitter.GetUserFollowing(user_link='https://twitter.com/Ultimateadi18'))
#print(Twitter.GetUserID(user_link='https://twitter.com/Ultimateadi18'))
#print(Twitter.GetUserweetCount('https://twitter.com/Ultimateadi18'))
#print(Twitter.GetRecentTweet('https://twitter.com/Ultimateadi18'))
#print(Youtube.GetChannelStats('UCJBtCUf_GEvlYeOwUSnCC0Q'))