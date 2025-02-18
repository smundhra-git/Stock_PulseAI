import pandas as pd
from src.database.base import *
from transformers import pipeline

# Import the FinBERT functions
from src.sentiment.sentimental_analysis import *

def fetch_sec_filings_for_testing(limit=5):
    """
    Fetch SEC filings from MongoDB for testing FinBERT sentiment analysis.
    Returns a Pandas DataFrame with 'content' and 'accession_number'.
    """
    collection = get_mongo_collection()

    # Fetch the latest SEC filings
    documents = collection.find({}, {"accession_number": 1, "content": 1}).limit(limit)
    df = pd.DataFrame(documents)

    if df.empty:
        print("No SEC filings found in the database for testing.")
    else:
        print(f"Retrieved {len(df)} SEC filings for testing.")
    
    return df

def store_sentiment_results(articles: pd.DataFrame):
    """
    Store sentiment analysis results (score and classification) in PostgreSQL.
    Uses INSERT ON CONFLICT to handle both new and existing records.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for _, row in articles.iterrows():
            print(f"📌 Storing: Accession {row['accession_number']} | Label: {row['sentiment_label']} | Score: {row['sentiment_score']}")

            cur.execute("""
                INSERT INTO sec_filings (accession_number, sentiment_label, sentiment_score, sentiment_class)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (accession_number) DO UPDATE
                SET sentiment_label = EXCLUDED.sentiment_label,
                    sentiment_score = EXCLUDED.sentiment_score,
                    sentiment_class = EXCLUDED.sentiment_class;
            """, (row["accession_number"], row["sentiment_label"], row["sentiment_score"], row["sentiment_class"]))

        conn.commit()
        print("✅ Sentiment results stored successfully in PostgreSQL.")
    except Exception as e:
        print("❌ Error storing sentiment results:", e)
    finally:
        cur.close()
        conn.close()



def test_finbert_sentiment_analysis():
    """
    End-to-end test: Fetch SEC filings → Run FinBERT Sentiment Analysis → Store Results.
    """
    # Initialize FinBERT model
    initialize_finbert()

    # Fetch test data from MongoDB
    test_articles = fetch_sec_filings_for_testing()

    if test_articles.empty:
        print("❌ No data available for testing.")
        return

    # Run FinBERT sentiment analysis
    analyzed_articles = analyze_sentiment_finbert_news(test_articles)

    # Store the results in PostgreSQL
    store_sentiment_results(analyzed_articles)

    # Retrieve and validate results
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT accession_number, sentiment_label, sentiment_score, sentiment_class FROM sec_filings LIMIT 5;")
    results = cur.fetchall()

    # Print retrieved data for debugging
    print("🔍 Retrieved Sentiment Results from PostgreSQL:", results)

    cur.close()
    conn.close()

    # Assert that results exist
    assert results, "❌ No sentiment results found in PostgreSQL."
    print("✅ Sentiment analysis test passed successfully!")


if __name__ == "__main__":
    test_finbert_sentiment_analysis()
