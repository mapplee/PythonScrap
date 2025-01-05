import os

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape_google_sheet(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    html_text = soup.prettify()

    match = re.search(r"https://docs\.google\.com/spreadsheets/d/e/[a-zA-Z0-9_\-]+/pub\?output=csv", html_text)
    if not match:
        print("Google Sheet URL not found in the page.")
        return None

    sheet_link = match.group(0)
    print(f"Google Sheet URL found: {sheet_link}")

    sheet_csv_url = sheet_link
    print(f"CSV download link: {sheet_csv_url}")

    csv_response = requests.get(sheet_csv_url, headers=headers)
    if csv_response.status_code != 200:
        print(f"Failed to fetch the Google Sheet CSV. Status code: {csv_response.status_code}")
        return None


     # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)
    # Save the CSV file
    csv_file = os.path.join('data',"fpl_differentials.csv")
    with open(csv_file, "wb") as file:
        file.write(csv_response.content)
    print(f"CSV data saved to {csv_file}")

    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Save the DataFrame as JSON
    json_file = os.path.join('data',"best_fpl_differentials.json")
    df.to_json(json_file, orient="records", indent=4)
    print(f"JSON data saved to {json_file}")

    return df

# Define the base URL for scraping
base_url = "https://www.fantasyfootballpundit.com/best-fpl-differentials/"

# Call the function to scrape Google Sheet data
df = scrape_google_sheet(base_url)

if df is not None:
    print("Data preview:")
    print(df.head())
