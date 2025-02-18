from src.database.base import get_mongo_collection, get_db_connection
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta

# Define SEC API headers once at the top
SEC_HEADERS = {
    "User-Agent": "StockPulseAI/1.0 (shlokmundhra@gmail.com)",  # Your actual email
    "Accept-Encoding": "gzip, deflate"
}

# This works
def get_cik_from_ticker(ticker: str) -> str:
    """
    Fetches the CIK number for a given stock ticker from the SEC EDGAR API.
    
    :param ticker: Stock ticker symbol (e.g., "AAPL" for Apple).
    :return: CIK number as a string (10 digits with leading zeros).
    """
    try:
        # Add delay for SEC rate limit
        time.sleep(0.1)
        
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {**SEC_HEADERS, "Host": "www.sec.gov"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            return None
        elif response.status_code != 200:
            return None

        cik_data = response.json()
        
        # Convert ticker to uppercase for comparison
        ticker = ticker.upper()
        
        # Find the matching company
        for company in cik_data.values():
            if company["ticker"] == ticker:
                # Format CIK to 10 digits with leading zeros
                return str(company["cik_str"]).zfill(10)
        
        return None
    
    except Exception as e:
        return None

#This works
def fetch_sec_filing(cik):
    """
    Fetch the latest SEC filings for a given entity using the SEC EDGAR API.
    :param cik: The 10-digit Central Index Key (CIK) including leading zeros.
    :return: JSON response containing the latest SEC filings.
    """
    # Ensure CIK is 10 digits with leading zeros
    cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    
    try:
        # Add delay for SEC rate limit
        time.sleep(0.1)
        
        headers = {**SEC_HEADERS, "Host": "data.sec.gov"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            return None
        elif response.status_code == 404:
            return None
        else:
            return None
    except Exception as e:
        return None

# Extract Relevant SEC Filings - Works
def fetch_sec_data(data):
    """Extracts and filters SEC filings from JSON response."""
    if not data:
        return None

    forms_filter = ['10-K', '10-Q', '8-K', 'DEF 14A', '13F', 'S1', 'FORM 4', '20F', '6K']
    filings = data.get("filings", {}).get("recent", {})
    
    df = pd.DataFrame({
        "Form Type": filings.get("form", []),
        "Date": filings.get("filingDate", []),
        "Accession Number": filings.get("accessionNumber", [])
    })

    df["Filing URL"] = df.apply(
        lambda row: f"https://www.sec.gov/Archives/edgar/data/{data['cik']}/{row['Accession Number'].replace('-', '')}/{row['Accession Number']}.txt",
        axis=1
    )

    return df[df["Form Type"].isin(forms_filter)]

def extract_filing_text(url):
    """Fetches and extracts full text from an SEC filing."""
    try:
        # Add delay for SEC rate limit
        time.sleep(0.1)
        
        headers = {**SEC_HEADERS, "Host": "www.sec.gov"}
        response = requests.get(url, headers=headers)

        if response.status_code == 403:
            return ""
        elif response.status_code != 200:
            return ""

        # Use lxml parser instead of html.parser for better performance
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except:
            # Fallback to html.parser if lxml fails
            soup = BeautifulSoup(response.text, "html.parser")

        # Extract text more safely
        try:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(line for line in lines if line)
            
            return text
        except Exception as e:
            return ""

    except Exception as e:
        return ""

# Store Filing Metadata in PostgreSQL
def store_metadata_postgres(cik, form_type, date, accession_number, sec_url):
    """Stores filing metadata in PostgreSQL."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO sec_filings (cik, form_type, filing_date, accession_number, sec_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (accession_number) DO NOTHING;
        """, (cik, form_type, date, accession_number, sec_url))
        conn.commit()
    except Exception as e:
        pass
    finally:
        cur.close()
        conn.close()

def store_filing_text_mongo(cik, form_type, accession_number, text):
    """Stores full SEC filing text in MongoDB, avoiding duplicates."""
    try:
        collection = get_mongo_collection()

        # Check if this accession number already exists
        existing_doc = collection.find_one({"accession_number": accession_number})
        if existing_doc:
            return

        # Insert only if it does not exist
        document = {
            "cik": cik,
            "form_type": form_type,
            "accession_number": accession_number,
            "content": text,
            "created_at": datetime.now()
        }
        collection.insert_one(document)
    except Exception as e:
        pass
# Retrieve Data for Analysis
def retrieve_filing_data(form_types=None, cik=None, after_date=None):
    """
    Retrieves SEC filings from PostgreSQL and full text from MongoDB.
    
    Args:
        form_types: List of SEC form types to filter
        cik: Company CIK number to filter
        after_date: Only retrieve filings after this date
    Returns:
        DataFrame containing filing details and text
    """
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT cik, form_type, filing_date, accession_number, sec_url 
        FROM sec_filings 
        WHERE 1=1
    """
    params = []

    if cik:
        query += " AND cik = %s"
        params.append(cik)

    if form_types:
        form_types_str = "', '".join(form_types)
        query += f" AND form_type IN ('{form_types_str}')"

    if after_date:
        query += " AND filing_date > %s"
        params.append(after_date)

    query += " ORDER BY filing_date DESC"

    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    conn.close()

    if not results:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(results, columns=["CIK", "Form Type", "Date", "Accession Number", "URL"])

    # Retrieve full text from MongoDB
    collection = get_mongo_collection()
    df["Full Text"] = df["Accession Number"].apply(
        lambda acc_num: collection.find_one({"accession_number": acc_num}, {"content": 1, "_id": 0})["content"]
        if collection.find_one({"accession_number": acc_num}) else ""
    )

    return df


# Main Execution Function
def process_sec_filings(cik_number):
    """
    Fetch, process, and store only new SEC filings for a given CIK.
    If no data exists, pull for 1 year; otherwise, pull only new filings.
    """
    last_filing_date = get_last_filing_date(cik_number)

    if last_filing_date:
        # Convert to pandas datetime for comparison
        start_date = pd.to_datetime(last_filing_date)
    else:
        start_date = pd.to_datetime(datetime.now() - timedelta(days=365))

    # Fetch SEC data
    sec_data = fetch_sec_filing(cik_number)
    filings_df = fetch_sec_data(sec_data)

    if filings_df is None or filings_df.empty:
        return

    # Convert dates to pandas datetime
    filings_df["Date"] = pd.to_datetime(filings_df["Date"])
    new_filings_df = filings_df[filings_df["Date"] > start_date]

    if new_filings_df.empty:
        return


    for _, row in new_filings_df.iterrows():
        form_type = row["Form Type"]
        accession_number = row["Accession Number"]
        filing_date = row["Date"].date()  # Convert to date for PostgreSQL
        sec_url = row["Filing URL"]

        try:
            # Check if filing already exists
            if check_filing_exists(accession_number):
                continue

            # Fetch Filing Text
            filing_text = extract_filing_text(sec_url)
            if not filing_text:
                continue

            # Store metadata in PostgreSQL
            store_metadata_postgres(cik_number, form_type, filing_date, accession_number, sec_url)

            # Store full filing text in MongoDB
            store_filing_text_mongo(cik_number, form_type, accession_number, filing_text)


        except Exception as e:
            continue


def store_sentiment_results(articles: pd.DataFrame):
    """
    Store sentiment analysis results in PostgreSQL.
    """
    conn = get_db_connection()  # Changed from get_pg_connection
    cur = conn.cursor()

    try:
        # First, add the columns if they don't exist
        cur.execute("""
            ALTER TABLE sec_filings 
            ADD COLUMN IF NOT EXISTS sentiment_label TEXT,
            ADD COLUMN IF NOT EXISTS sentiment_score FLOAT,
            ADD COLUMN IF NOT EXISTS sentiment_class TEXT;
        """)
        
        for _, row in articles.iterrows():
            cur.execute("""
                UPDATE sec_filings
                SET sentiment_label = %s, 
                    sentiment_score = %s, 
                    sentiment_class = %s
                WHERE accession_number = %s;
            """, (
                row["sentiment_label"], 
                row["sentiment_score"], 
                row["sentiment_class"], 
                row["accession_number"]
            ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def create_sec_filings_table():
    """Creates the SEC filings metadata table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sec_filings (
                id SERIAL PRIMARY KEY,
                cik VARCHAR(10),
                form_type VARCHAR(10),
                filing_date DATE,
                accession_number VARCHAR(20) UNIQUE,
                sec_url TEXT,
                sentiment_label TEXT,
                sentiment_score FLOAT,
                sentiment_class TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        pass
    finally:
        cur.close()
        conn.close()


def clear_mongodb_data():
    """Clears all data from the MongoDB collection."""
    try:
        collection = get_mongo_collection()
        result = collection.delete_many({})
    except Exception as e:
        pass


def get_last_filing_date(cik_number):
    """
    Retrieves the latest filing date for a given CIK from PostgreSQL.
    
    Args:
        cik_number: CIK number of the company
    Returns:
        datetime: Latest filing date or None if no filings exist
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        query = "SELECT MAX(filing_date) FROM sec_filings WHERE cik = %s;"
        cur.execute(query, (cik_number,))
        last_date = cur.fetchone()[0]
        return last_date
    except Exception as e:
        return None
    finally:
        cur.close()
        conn.close()


def check_filing_exists(accession_number):
    """
    Check if a filing already exists in the database.
    
    Args:
        accession_number: SEC filing accession number
    Returns:
        bool: True if filing exists, False otherwise
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query = "SELECT EXISTS(SELECT 1 FROM sec_filings WHERE accession_number = %s);"
        cur.execute(query, (accession_number,))
        exists = cur.fetchone()[0]
        return exists
    except Exception as e:
        return False
    finally:
        cur.close()
        conn.close()


def main(ticker: str = None):
    """
    Process SEC filings for a given ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL" for Apple)
    Returns:
        pd.DataFrame: DataFrame containing the processed filings, or None if error
    """
    try:        
        # Create necessary tables
        create_sec_filings_table()
        
        if not ticker:
            return None
            
        
        # Get CIK number
        cik_number = get_cik_from_ticker(ticker)
        if not cik_number:
            return None
                    
        # Add delay between operations
        time.sleep(1)
        
        # Process the filings
        process_sec_filings(cik_number)

        # Retrieve and analyze filings
        forms_filter = ['10-K', '10-Q', '8-K', 'DEF 14A', '13F', 'S1', 'FORM 4', '20F', '6K']
        filings_df = retrieve_filing_data(form_types=forms_filter, cik=cik_number)

        if filings_df.empty:
            return None

        return filings_df

    except KeyboardInterrupt:
        return None
    except Exception as e:
        return None


def test_sec_optimization():
    """Test the SEC filing optimization process."""
    try:
        ticker = "AAPL"  # Use Apple as test case

        # 1. Clear existing data
        collection = get_mongo_collection()
        mongo_count = collection.count_documents({})
        
        clear = input("Clear existing data? (y/n): ").lower()
        if clear == 'y':
            clear_mongodb_data()
            
            # Also clear PostgreSQL
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM sec_filings;")
            conn.commit()
            cur.close()
            conn.close()

        # 2. First Run - Should pull 1 year of data
        main(ticker)
        
        # Check counts
        collection = get_mongo_collection()
        mongo_count = collection.count_documents({})
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sec_filings;")
        pg_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        
        # 3. Second Run - Should only pull new filings
        main(ticker)
        
        # Check counts again
        collection = get_mongo_collection()
        new_mongo_count = collection.count_documents({})
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sec_filings;")
        new_pg_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
 
        # 4. Check latest filing dates
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT MIN(filing_date), MAX(filing_date) 
            FROM sec_filings 
            WHERE cik = (SELECT cik FROM sec_filings LIMIT 1);
        """)
        min_date, max_date = cur.fetchone()
        cur.close()
        conn.close()

        
        # 5. Check form types distribution
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT form_type, COUNT(*) 
            FROM sec_filings 
            GROUP BY form_type 
            ORDER BY COUNT(*) DESC;
        """)
        form_counts = cur.fetchall()
        cur.close()
        conn.close()
        

        
    except Exception as e:
        pass

if __name__ == "__main__":
    # Add test option
    mode = input("Run test? (test/normal): ").lower()
    if mode == 'test':
        test_sec_optimization()
    else:
        ticker = input("Enter stock ticker (e.g., AAPL): ").upper()
        main(ticker)