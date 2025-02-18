from src.sentiment.fetch_data import *
from src.sentiment.sentimental_analysis import *
from src.database.sec_files import *

#NEWS SENTIMENT DONE
def news_sentiment(query:str)->float:
    """
    This function takes in a company ticker and returns the sentment on
    NEWSAPI (Currently 1d delyaed)
    Shall use finBert (50%) and Vader (50%) weight respectively
    """
        
    news_articles = fetch_financial_news(query, count=100)
    articles_df = pd.DataFrame(news_articles)
    articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
    articles_df = articles_df.sort_values('publishedAt', ascending=False)
    articles_df = articles_df.drop_duplicates(subset=['title'])
    articles_df = articles_df.head(50) 


    articles_df = analyze_sentiment_vader_news(articles_df)
    articles_df = analyze_sentiment_finbert_news(articles_df) 

    articles_df['score'] = 0

    for index, row in articles_df.iterrows():
        vader_score = ((row['compound']*50) + 50) 
        finbert_score = row['sentiment_score']
        articles_df['score'] = vader_score*0.8 +finbert_score*0.2

    news_sentiment_score = articles_df['score'].sum() / 50
    return news_sentiment_score
    

def reddit_sentiment(query:str):
    """
    This function takes in a company ticker and returns the sentment on
    NEWSAPI (Currently 1d delyaed)
    and Reddit
    Duture integration - X
    """

    ### REDDIT POSTS
    reddit_posts = fetch_reddit_posts(query, count=100)

    reddit_posts_df = pd.DataFrame(reddit_posts)
    reddit_posts_df['created_utc'] = pd.to_datetime(reddit_posts_df['created_utc'], unit='s')
    reddit_posts_df = reddit_posts_df.sort_values('created_utc', ascending=False)
    reddit_posts_df = reddit_posts_df.head(50)
    reddit_posts_df = analyze_sentiment_vader_reddit(reddit_posts_df)
    reddit_sentiment_score = (reddit_posts_df['compound'].sum()/50 * 50) + 50

    return reddit_sentiment_score

def sec_sentiment(query: str) -> float:
    """
    Fetches SEC filings for a given company ticker, analyzes sentiment,
    and returns a sentiment score (0-100).

    :param query: Stock ticker symbol (e.g., "AAPL" for Apple).
    :return: Sentiment score (0-100).
    """
    from src.database.sec_files import main as process_sec_filings
    
    # Process SEC filings
    filings_df = process_sec_filings(query)
    if filings_df is None:
        return None

    
    # Ensure we have the 'Full Text' column for analysis
    if 'Full Text' not in filings_df.columns:
        return None
        
    # Rename 'Full Text' to 'content' for sentiment analysis
    filings_df = filings_df.rename(columns={'Full Text': 'content'})
    
    try:
        # Run sentiment analysis
        analyzed_filings = analyze_sentiment_finbert_sec(filings_df)
        
        if 'sentiment_score' not in analyzed_filings.columns:
            return None
            
        # Compute Final Sentiment Score (0-100)
        sec_sentiment_score = analyzed_filings['sentiment_score'].mean()
        
        # Scale the score to 0-100 if needed
        if sec_sentiment_score < 0 or sec_sentiment_score > 100:
            sec_sentiment_score = (sec_sentiment_score + 1) * 50  # Scale from [-1,1] to [0,100]
            
        return sec_sentiment_score
        
    except Exception as e:
        return None



def main():
    query = input("Enter a financial topic (e.g., Tesla, Fed, etc.): ")
    #Equal weightage for all sentiment scores
    news_sentiment_score = news_sentiment(query)
    reddit_sentiment_score = reddit_sentiment(query)
    sec_sentiment_score = sec_sentiment(query)

    sentiment_score = (news_sentiment_score + reddit_sentiment_score + sec_sentiment_score) / 3
    print(f"Final Sentiment Score: {sentiment_score}")

if __name__ == '__main__':
    main()

