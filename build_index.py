import os
import time
import requests
import duckdb
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

SITEMAP_URL = "https://open.toronto.ca/page-sitemap.xml"
DB_FILE = "opendata.db"
SQL_FILE = "opendata.sql"

def get_sitemap_urls():
    """Fetches and parses the sitemap to extract URLs."""
    urls = []
    try:
        response = requests.get(SITEMAP_URL)
        response.raise_for_status()
        xml = response.content.decode('utf-8')
        xml_lines = xml.splitlines()
        xml_lines = [line for line in xml_lines if '<?xml' not in line]
        xml = '\n'.join(xml_lines)
        soup = BeautifulSoup(xml, "xml")
        for loc in soup.find_all("loc"):
            urls.append(loc.text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap: {e}")
    return urls

from playwright.sync_api import sync_playwright

def fetch_and_process_page(url):
    """Fetches a page using Playwright and converts its content to Markdown."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle")
            content = page.content()
            return md(content)
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            return None
        finally:
            browser.close()

def build_index():
    """Builds the search index and saves it to a DuckDB SQL file."""
    urls = get_sitemap_urls()
    if not urls:
        print("No URLs found in the sitemap. Exiting.")
        return

    # Remove existing DB file to ensure a fresh start
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    con = duckdb.connect(DB_FILE)
    con.execute("""
        CREATE TABLE pages (
            url VARCHAR PRIMARY KEY,
            summary VARCHAR
        );
    """)

    delay = int(os.environ.get("RATE_LIMIT_DELAY", 6))
    for i, url in enumerate(urls):
        print(f"Processing {url}...")
        summary = fetch_and_process_page(url)
        if summary:
            con.execute("INSERT INTO pages (url, summary) VALUES (?, ?)", (url, summary))
        if i < len(urls) - 1:
            time.sleep(delay)

    # Export to SQL
    con.execute(f"EXPORT DATABASE '.' (FORMAT SQL, ENCODING 'UTF-8');")

    con.close()

    # Rename the exported file
    if os.path.exists('export.sql'):
        if os.path.exists(SQL_FILE):
            os.remove(SQL_FILE)
        os.rename('export.sql', SQL_FILE)


if __name__ == "__main__":
    build_index()
