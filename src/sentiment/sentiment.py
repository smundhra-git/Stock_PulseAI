from src.sentiment.fetch_data import *
from src.sentiment.sentimental_analysis import *


def sentiment(query:str):
    """
    This function takes in a company ticker and returns the sentment on
    NEWSAPI (Currently 1d delyaed)
    and Reddit
    Duture integration - X
    """

    # NEWS ARTICLES

    news_articles = fetch_financial_news(query, count=100)
    articles_df = pd.DataFrame(news_articles)
    articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
    articles_df = articles_df.sort_values('publishedAt', ascending=False)
    articles_df = articles_df.drop_duplicates(subset=['title'])
    articles_df = articles_df.head(50) #keep only the latest 50
    articles_df = analyze_sentiment_vader_news(articles_df)
    # for the 50 articles, sum the compound scores
    #this compound score * 100 will be on a scale of -100 to 100
    # divide this by 2 and add 50, and we have a score between 0 and 100
    # this will be the news sentiment score
    news_sentiment_score = articles_df['compound'].sum() / 2 + 50

    ### REDDIT POSTS
    reddit_posts = fetch_reddit_posts(query, count=100)
    # Reddit posts df are ['title', 'selftext', 'created_utc']
    # we need to convert the created_utc to a datetime object
    # and then sort the dataframe by the created_utc
    # and then keep only the latest 50
    # and then analyze the sentiment of the selftext
    # and then sum the compound scores
    # and then divide by 2 and add 50, and we have a score between 0 and 100
    # this will be the reddit sentiment score
    reddit_posts_df = pd.DataFrame(reddit_posts)
    reddit_posts_df['created_utc'] = pd.to_datetime(reddit_posts_df['created_utc'], unit='s')
    reddit_posts_df = reddit_posts_df.sort_values('created_utc', ascending=False)
    reddit_posts_df = reddit_posts_df.head(50)
    reddit_posts_df = analyze_sentiment_vader_reddit(reddit_posts_df)
    reddit_sentiment_score = reddit_posts_df['compound'].sum() / 2 + 50

    return {
        "news_sentiment_score": news_sentiment_score,
        "reddit_sentiment_score": reddit_sentiment_score
    }




def main():
    query = input("Enter a financial topic (e.g., Tesla, Fed, etc.): ")
    s = sentiment(query)
    print(s)

if __name__ == '__main__':
    main()

