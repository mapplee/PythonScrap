import os

import requests
from bs4 import BeautifulSoup
import json

# URL of the webpage
url = "https://www.fantasyfootballpundit.com/fantasy-premier-league-team-news/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36"
}

# Function to extract the predicted lineup for a single team
def extract_lineup(team_div):
    # Extract team name
    team_name = team_div.find('h2')  # This assumes each team's name is inside an <h2> tag
    if team_name:
        team_name = team_name.text.strip()
    else:
        team_name = None

    # Extract the table rows for predicted players and potential starters
    players_data = []
    potential_starters = []
    tables = team_div.find_all('table')

    # Extract players
    for table in tables:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 3:
                player_name = columns[0].text.strip()
                position = columns[1].text.strip()
                starting_percentage = columns[2].text.strip()

                # Check if the player data is part of the predicted lineup or potential starters
                if "Potential Starters" not in player_name:
                    players_data.append({
                        "player": player_name,
                        "position": position,
                        "starting_percentage": starting_percentage
                    })
                else:
                    potential_starters.append({
                        "player": player_name,
                        "position": position,
                        "starting_percentage": starting_percentage
                    })

    return {
        "team_name": f"{team_name}",
        "players": players_data,  # Only first 11 players are starters
        "Potential Starters": potential_starters
    }

# Main scraping function
def scrape_team_news(url, headers):
    try:
        # Send a GET request with headers
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all team lineup sections
        teams_divs = soup.find_all('div', class_="wp-block-column is-layout-flow wp-block-column-is-layout-flow")

        # Extract the predicted lineups for each team
        all_teams_data = []
        for team_div in teams_divs:
            team_lineup = extract_lineup(team_div)
            all_teams_data.append(team_lineup)

        # List to hold the reformatted data
        odd_index_data = []

        # Iterate over the list and update the odd indices
        for i in range(1, len(all_teams_data), 2):
            # Get the team name from the previous even index
            team_name_from_even_index = all_teams_data[i - 1]['team_name'] if i - 1 < len(all_teams_data) else None
            # Set the team name for the current odd index
            all_teams_data[i]['team_name'] = team_name_from_even_index

            # Now split players into first 11 (players) and the rest into Potential Starters
            players = all_teams_data[i]['players'][:11]  # First 11 players
            potential_starters = all_teams_data[i]['players'][11:]  # Rest of the players

            # Update the players and Potential Starters
            all_teams_data[i]['players'] = players
            all_teams_data[i]['Potential Starters'] = potential_starters

            # Append the odd index entry with updated players to the new list
            odd_index_data.append(all_teams_data[i])

        os.makedirs('data', exist_ok=True)

        # Save the reformatted odd-indexed data to a new JSON file
        with open(os.path.join('data','predicted_lineups.json'), 'w', encoding='utf-8') as json_file:
            json.dump(odd_index_data, json_file, indent=4, ensure_ascii=False)

        print("Scraping completed and reformatted data saved to 'predicted_lineups.json'.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

scrape_team_news(url, headers)
