import os

import requests
import re
import pandas as pd
from io import StringIO

# URL of the target webpage
url = "https://www.fantasyfootballpundit.com/premier-league-penalty-takers/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36"
}

# Send a GET request with headers
response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"Failed to fetch the webpage. Status code: {response.status_code}")
    exit()

html_content = response.text

# Extract the Google Sheets URL using a regex pattern
sheet_url_pattern = re.search(r'"sheet":\s*"(https://docs.google.com/spreadsheets/[^\"]+)"', html_content)
if not sheet_url_pattern:
    print("Sheet URL not found in the HTML content.")
    exit()

sheet_url = sheet_url_pattern.group(1)
print(f"Extracted sheet URL: {sheet_url}")

# Fetch the CSV data from the sheet URL
csv_response = requests.get(sheet_url)
if csv_response.status_code != 200:
    print(f"Failed to fetch the CSV file. Status code: {csv_response.status_code}")
    exit()

# Save the CSV data into a DataFrame
csv_data = StringIO(csv_response.text)
df = pd.read_csv(csv_data)

# Check if both "Team" and "Penalty Taker" columns are present
if "Team" not in df.columns or "Penalty Taker" not in df.columns:
    # If the necessary columns are missing, save as "other" in both CSV and JSON formats
    print("Missing necessary columns. Saving data as 'other.csv' and 'other.json'.")
    df.to_csv("other.csv", index=False)
    df.to_json("other.json", orient="records", lines=True)
else:
    # Clean the "Penalty Taker" column to remove line breaks and split into lists
    df['Penalty Taker'] = df['Penalty Taker'].str.split(r'\n').apply(lambda x: [item.strip() for item in x])

    # Clean the "Last 5 Pens" column to format the goals more clearly
    df['Last 5 Pens'] = df['Last 5 Pens'].str.replace(r'\n', ', ', regex=True)
    df['Last 5 Pens'] = df['Last 5 Pens'].str.replace(r'\/', '/', regex=True)

    # Ensure no trailing commas in "Last 5 Pens"
    df['Last 5 Pens'] = df['Last 5 Pens'].str.rstrip(', ')



    os.makedirs('data', exist_ok=True)
    # Save the cleaned data as both CSV and JSON
    df.to_csv(os.path.join('data',"penalty_takers.csv"),index=False)
    df.to_json(os.path.join('data',"penalty_takers.json"), orient="records", lines=False)

# Print a confirmation message
print(f"Data saved as {'other.csv and other.json' if 'Team' not in df.columns or 'Penalty Taker' not in df.columns else 'penalty_takers.csv and penalty_takers.json'}")
