from src.sentiment.fetch_data import *
from src.database.sentiment import *
import re
from nltk.corpus import stopwords
import string


def preprocess_text(text: str) -> str:
    """
    Preprocess the input text: remove URLs, non-alphabetic characters, convert to lowercase.
    """
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower().strip()


def preprocess_text_dict(text: dict):
    """
    Coverts a dict into a string and processes it
    """
    text = text['title'] + ' ' + text['selftext']
    return preprocess_text(text)