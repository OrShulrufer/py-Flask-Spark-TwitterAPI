from tweepy import API
from tweepy import Cursor
import sys, errno
from textblob import TextBlob
import twitter_credentials
import numpy as np
import pandas as pd
import re
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import datetime


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator:

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


# # # # TWITTER STREAMER # # # #
class TwitterStreamer:
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.twitter_authentication = TwitterAuthenticator()

    def stream_tweets(self, c_socket, hash_tag_list):
        # This handles Twitter authentication and the connection to Twitter Streaming API
        listener = TwitterListener(c_socket)
        auth = self.twitter_authentication.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self, c_socket):
        self.client_socket = c_socket
        self.tw = TweetAnalyzer()

    def on_data(self, data):
        try:
            msg = json.loads(data)
            str_msg = str(msg['text'].encode('utf-8'))
            '''
            if "donald" in str_msg:
                with open("search_files/ddd.txt", "w") as f:
                    f.write(self.tw.clean_tweet(str_msg))
                    print(str_msg)
                f.close()
            '''
             # print(str_msg)
            self.client_socket.send(msg['text'].encode('utf-8'))
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            return True
        except KeyboardInterrupt:
            print("It's ok")
            return True
        except IOError as e:
            if e.errno == errno.EPIPE:
                print("Pipe Eror")
            return True

    def on_error(self, status):
        print(status)
        return True


class TweetAnalyzer:
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df


def get_sentiment_multiplide_by_retweet(tweet):
    return int(tweet.retweet_count) * int(tweet_analyzer.analyze_sentiment(tweet.text))


def get_values_by_hashtag(hash_tag, sc):
    # get tweets for 1 hash tag starting from date
    rdd = sc.parallelize(api.search(q=hash_tag, from_date=startDate))

    # make rdd list of tuples (text of tweet, sentiment multiplied by re tweet
    # and getting read of duplicate tweets (bots)
    rdd_dictionary_set = rdd.map(lambda x: (x.text, get_sentiment_multiplide_by_retweet(x))).reduceByKey(lambda a, b: a)

    # make rdd dictionary with Set of key's
    rdd_values = rdd_dictionary_set.values()

    sum_of_values = 0
    # you can not activate reduce on empty rdd
    if not rdd_values.isEmpty():
        # get sum of all sentiment multiplied by re tweet values
        sum_of_values = rdd_values.reduce(lambda x, y: x + y)
        #print(hash_tag, " ", sum_of_values)

    return sum_of_values


# spark context definitio
sc = SparkContext("local[2]", "Twitter Demo")
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 10)

# for displaying all columns of data frame
pd.set_option('display.max_columns', None)


# creating
twitter_client = TwitterClient()
tweet_analyzer = TweetAnalyzer()

# we will get tweets starting this date
startDate = datetime.datetime(2019, 8, 1, 0, 0, 0)

# get api from twitter
api = twitter_client.get_twitter_client_api()


def turn_on_graph_app(hash_tag_list):
    value_list = []
    # get values for every hash tag in hash tag list
    for hash_tag in hash_tag_list:
        value_list.append(get_values_by_hashtag(hash_tag, sc))
    return value_list



