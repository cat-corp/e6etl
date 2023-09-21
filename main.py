from urllib.request import Request, urlopen
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import psycopg2
import shutil
import base64
import json
import gzip
import os

import schemas

load_dotenv()

USERNAME = os.getenv("USERNAME")
API_KEY = os.getenv("API_KEY")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

DOWNLOAD_BASE_DIR = "./downloads/"
USER_AGENT = f"etl/0.5 ({USERNAME})"

# Run at 5AM EST

def main():
    print("Downloading CSV files...")
    download_csv_files(list(schemas.tables))
    print("Done downloading CSV files. Pushing to database...")
    conn = psycopg2.connect(f"host='{POSTGRES_HOST}' port='5432' dbname='{POSTGRES_DB_NAME}' user='{POSTGRES_USER}' password='{POSTGRES_PASSWORD}'")
    conn.cursor().execute("DROP INDEX IF EXISTS tag_string_idx;")
    for table in schemas.tables:
        upload_table(conn, table, schemas.tables[table])
    print("Rebuilding tag index...")
    conn.cursor().execute("""
            CREATE INDEX IF NOT EXISTS tag_string_idx ON posts USING GIN (string_to_array(tag_string, ' '));
        """)            
    conn.commit()
    conn.close()
    print("Done.")

def download_csv_files(tables):
    base_url = "https://e621.net/db_export/"

    today = datetime.today().strftime("%Y-%m-%d")
    urls = [ (table, f'{base_url}{table}-{today}.csv.gz') for table in tables ]

    # Create download directory if it doesn't exist
    Path(DOWNLOAD_BASE_DIR).mkdir(parents=True, exist_ok=True)

    # Download and decompress csv for each table
    credentials = base64.b64encode(f"{USERNAME}:{API_KEY}".encode("ascii"))
    basic_auth = f"Basic {credentials}"

    for (table, url) in urls:
        print(f"Downloading {table} ({url})...")
        req = Request(url)
        req.add_header("User-Agent", USER_AGENT)
        req.add_header("Authorization", basic_auth)
        with urlopen(req) as download, open(f"{DOWNLOAD_BASE_DIR}{table}.csv.gz", "wb") as file:
            shutil.copyfileobj(download, file)

def upload_table(conn, table, columns):
    # Rebuild table
    conn.cursor().execute(f"""
        CREATE TABLE IF NOT EXISTS {table}
        (
            {columns}
        );
    """)
    conn.cursor().execute(f"TRUNCATE TABLE {table}")
    conn.commit()

    print(f"Copying {table}...")

    with open(f"{DOWNLOAD_BASE_DIR}{table}.csv.gz",  "rb") as posts_file:
        with conn.cursor() as cur:
            decompressed = gzip.GzipFile(fileobj=posts_file)
            cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER", decompressed)
            conn.commit()

if __name__ == "__main__":
    req = Request(WEBHOOK_URL)
    req.method = "POST"
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    try:
        main()
        urlopen(req, data=json.dumps({ "content": "e621 ETL completed successfully." }).encode("utf-8"))
    except Exception as e:
        urlopen(req, data=json.dumps({"content": f"e621 ETL failed: ```python\n{e}```" }).encode("utf-8"))