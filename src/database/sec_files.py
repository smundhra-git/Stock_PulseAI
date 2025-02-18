from src.database.base import get_mongo_collection, get_db_connection
import pandas as pd
import requests
from bs4 import BeautifulSoup

#for SEC
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}


def fetch_sec_filing(cik):
    """
    Fetch the latest SEC filings for a given entity using the SEC EDGAR API.
    :param cik: The 10-digit Central Index Key (CIK) including leading zeros.
    :return: JSON response containing the latest SEC filings.
    """
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}")
        return None

# Extract Relevant SEC Filings
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
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch filing. Status Code: {response.status_code}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()



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
        print(f" Error storing in PostgreSQL: {e}")
    finally:
        cur.close()
        conn.close()

def store_filing_text_mongo(cik, form_type, accession_number, text):
    """Stores full SEC filing text in MongoDB, avoiding duplicates."""
    collection = get_mongo_collection()

    # Check if this accession number already exists
    existing_doc = collection.find_one({"accession_number": accession_number})
    if existing_doc:
        print(f"🔹 Skipping {form_type} - {accession_number}, already exists in MongoDB.")
        return

    # Insert only if it does not exist
    document = {
        "cik": cik,
        "form_type": form_type,
        "accession_number": accession_number,
        "content": text
    }
    collection.insert_one(document)
    print(f" Stored {form_type} - {accession_number} in MongoDB")


# Retrieve Data for Analysis
def retrieve_filing_data(form_type=None):
    """Retrieves SEC filings from PostgreSQL and full text from MongoDB."""
    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT cik, form_type, filing_date, accession_number, sec_url FROM sec_filings"
    if form_type:
        query += f" WHERE form_type = '{form_type}'"

    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()

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
    """Fetches, processes, and stores SEC filings for a given CIK."""
    sec_data = fetch_sec_filing(cik_number)
    filings_df = fetch_sec_data(sec_data)

    if filings_df is not None:
        for _, row in filings_df.iterrows():
            cik = cik_number
            form_type = row["Form Type"]
            date = row["Date"]
            accession_number = row["Accession Number"]
            sec_url = row["Filing URL"]

            # Store metadata in PostgreSQL
            store_metadata_postgres(cik, form_type, date, accession_number, sec_url)

            # Fetch & Store full filing text in MongoDB
            filing_text = extract_filing_text(sec_url)
            store_filing_text_mongo(cik, form_type, accession_number, filing_text)

        print(" All filings processed and stored successfully!")

if __name__ == "__main__":
    cik_number = "0000320193"  # Apple Inc.
    
    # Step 1: Fetch & Store SEC Filings
    process_sec_filings(cik_number)
    
    # Step 2: Retrieve & Analyze Data
    filings_df = retrieve_filing_data("10-K")  # Example: Fetch only 10-K filings
    print(filings_df.head())