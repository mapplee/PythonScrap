import csv
import json
import os

import requests
from bs4 import BeautifulSoup

# URL of the webpage
url = "https://www.fantasyfootballpundit.com/fpl-captain-picks-gameweek/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36"
}


# Main scraping function
def scrape_team_news(url, headers):
    try:
        # Send a GET request with headers
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        script_tag = soup.find('script', string=lambda x: x and 'https://docs.google.com/spreadsheets' in x)
        if not script_tag:
            print("Could not find data source!")
            exit()

        # Extract the CSV URL from the script
        csv_url_start = script_tag.text.find("https://docs.google.com/spreadsheets")
        csv_url_end = script_tag.text.find('output=csv') + len('output=csv')
        csv_url = script_tag.text[csv_url_start:csv_url_end]

        if not csv_url:
            print("CSV URL not found!")
            exit()

        # Fetch the CSV data
        csv_response = requests.get(csv_url)
        if csv_response.status_code != 200:
            print("Failed to fetch the CSV file!")
            exit()

        # Ensure the 'data' directory exists
        os.makedirs('data', exist_ok=True)

        # Specify the full path to the 'data' directory and the desired CSV file name
        csv_filename_path = os.path.join('data', "fpl_captain_data.csv")
        # Save the data into a CSV file
        with open(csv_filename_path, 'w', newline='', encoding='utf-8') as file:
            file.write(csv_response.text)

        print(f"Data has been saved to {csv_filename_path}")

        # Parse CSV data
        csv_data = csv_response.text.splitlines()
        reader = csv.DictReader(csv_data)

        # Define the JSON output structure
        json_data = []
        for row in reader:
            json_data.append({
                "Player": row.get("Name", ""),
                "Predicted Points": row.get("xPredicted", ""),
                "Next Fixture": row.get("Fixture", ""),
                "Pick %": row.get("Ownership", ""),
                "Assist Odds": row.get("AnytimeAssistDGW", ""),
                "Goal Odds": row.get("AnytimeGoalDGW", ""),
                "Anytime Return": row.get("AnytimeReturn", "")
            })



        # Save the data to a JSON file
        json_file_name_path = os.path.join('data', "fpl_captain_data.json")

        with open(json_file_name_path, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)

        print(f"Data has been saved to {json_file_name_path}")


        # Print the raw HTML content to verify if the table is there

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


# Run the scraper
scrape_team_news(url, headers)
