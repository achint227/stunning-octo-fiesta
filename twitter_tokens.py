# Importing Libraries
# Tweepy for accessing Twitter APIs
import tweepy
import argparse
import pandas as pd
# Natural Language Toolkit libraries
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from datetime import datetime

# Global Variables
TAG_DICT = {"J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV}
LEMMATIZER = WordNetLemmatizer()

# Initializing Stop words from NLTK library
STOP_WORDS = stopwords.words('english')
BEARER_TOKEN = '<TWITTER_API_BEARER_TOKEN>'


# Function to lemmatize tokens after preprocessing
def lemmatized_tokens(s):
    words = list(filter(lambda x: str.isalpha(x) and len(x) > 2,
                        s.lower().replace('-', ' ').replace('.', '').replace(',', '').split()))
    res = set()
    for word, tag in pos_tag(words):
        res.add(LEMMATIZER.lemmatize(word, TAG_DICT.get(tag[0].upper(), wordnet.NOUN)))
    return [w for w in res if w not in STOP_WORDS]


# Function to extract information from tweets
def analyze_tweets(bearer_token, twitter_id):
    client = tweepy.Client(bearer_token=bearer_token)
    pages = tweepy.Paginator(client.get_users_tweets, twitter_id, max_results=100,
                             tweet_fields=['created_at', 'public_metrics']).flatten()
    retweet_count = {}
    count = {}
    for page in pages:
        text = page.data['text']
        retweets = page.data['public_metrics']['retweet_count']
        for token in lemmatized_tokens(text):
            if token in retweet_count:
                retweet_count[token] += retweets
            else:
                retweet_count[token] = retweets
            if token in count:
                count[token] += 1
            else:
                count[token] = 1
    impact = {}
    for token in count:
        impact[token] = retweet_count[token] // count[token]
    return impact


# Wrapper function for Tweet data extraction
def analyze_tweets_from_screen_name(bearer_token, screen_name, file_name=None):
    auth = tweepy.OAuth2BearerHandler(bearer_token)
    api = tweepy.API(auth)
    twitter_id = api.get_user(screen_name=screen_name).id_str
    impact = analyze_tweets(bearer_token, twitter_id)
    if not file_name:
        file_name = screen_name + '_' + datetime.now().strftime("%Y-%m-%d %H_%M_%S") + '.csv'
    if impact:
        df = pd.DataFrame({'Token': impact.keys(), 'Impact': impact.values()})
        df.sort_values(by=['Impact'], inplace=True, ascending=False)
        df.to_csv(file_name, index=False)
        return
    print('Error')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('x', type=str)
    args = parser.parse_args()
    analyze_tweets_from_screen_name(BEARER_TOKEN, args.x)
