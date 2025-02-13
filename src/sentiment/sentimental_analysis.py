"""
Classify is the sentimental is bullish or bearish
use of NLP, text analysis and computational liguistics
We will use VADER (future -> build our own lexicon)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import seaborn as sns
import seaborn as sns
import math
import datetime
import re
import yfinance as yf
import nltk
from datetime import date, timedelta
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.downloader.download('vader_lexicon')
from textblob import TextBlob
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
from sentiment.fetch_data import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiment.process import *

# https://www.geeksforgeeks.org/python-sentiment-analysis-using-vader/
def analyze_sentiment_vader(articles: pd.DataFrame) -> pd.DataFrame:
    """
    Use VADER to compute sentiment scores for each row in the DataFrame.
    Assumes the text to analyze is in the 'content' column.
    Adds sentiment columns ('neg', 'neu', 'pos', 'compound') to the DataFrame,
    and classifies sentiment as 'bullish', 'bearish', or 'neutral' based on the compound score.
    """
    sid_obj = SentimentIntensityAnalyzer()

    # Apply sentiment analysis to the 'content' column after preprocessing
    def get_scores(text):
        text = preprocess_text(text)
        return sid_obj.polarity_scores(text)

    # Get scores as a Series of dictionaries, then expand into a DataFrame
    scores_series = articles['content'].apply(get_scores)
    scores_df = pd.DataFrame(scores_series.tolist())
    articles = pd.concat([articles, scores_df], axis=1)

    # Classify sentiment based on compound score
    def classify_sentiment(compound):
        if compound >= 0.05:
            return "bullish"
        elif compound <= -0.05:
            return "bearish"
        else:
            return "neutral"

    articles['sentiment_class'] = articles['compound'].apply(classify_sentiment)
    return articles

def main():
    query = input("Enter a financial topic (e.g., Tesla, Fed, etc.): ")
    # Fetch news articles (this returns a list of dictionaries)
    news_articles = fetch_financial_news(query, count=100)
    
    # Convert list of dictionaries to a DataFrame
    articles_df = pd.DataFrame(news_articles)
    
    # If desired, you can sort the DataFrame by date (fetch_financial_news already sorted it)
    # articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
    # articles_df = articles_df.sort_values('publishedAt', ascending=False)
    
    # Analyze sentiment using VADER and classify as bullish or bearish
    articles_df = analyze_sentiment_vader(articles_df)
    
    # Display the first few rows
    print(articles_df.head())

if __name__ == '__main__':
    main()