import json
import csv
import time
import argparse
from urllib.request import urlopen
from urllib.error import HTTPError

class APIError(Exception):
    pass

class DataError(Exception):
    pass

def fetch_match_data(j, match_id, platform, api_key):
    url = f"https://{platform}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    
    try:
        response = urlopen(url)
    except HTTPError as e:
        print(f"\n{e.reason} on record {j}")
        raise APIError
    else:
        try:
            data = json.loads(response.read())
            data_row = [
                    j,
                    data['metadata']['matchId'],
                    data['info']['gameCreation'],
                    data['info']['gameMode'],
                    data['info']['gameType'],
                    data['info']['gameVersion'],
                    data['info']['mapId'],
                    data['info']['queueId']
                ]
            for i in range(0,10):
                data_row.append(data['info']['participants'][i]['puuid'])
                data_row.append(data['info']['participants'][i]['championName'])
                data_row.append(data['info']['participants'][i]['win'])
            return data_row
        except Exception as e:
            print(f"\n{e} on record {j}")
            raise DataError


def main():
    parser = argparse.ArgumentParser(description="Extract match data from match IDs.")
    parser.add_argument("--api_key", required=True, help="Riot Games API key.")
    parser.add_argument("--platform", required=True, help="Platform for API requests (e.g., americas, europe).")
    parser.add_argument("--input", required=True, help="Path to the input match ID CSV file.")
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    parser.add_argument("--delay", required=True, help="Delay to match Riot Games API (hint: start with 1.2 and titrate down).")
    parser.add_argument("--start", required=True, help="Scraping may pause abruptly. Start with 0 if beginning to scrape; otherwise, input the index number from previous attempt.")
    
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        match_ids = {row[i] for row in csv.reader(f) for i in range(1, len(row))}

    with open(args.output, 'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        for i in range(args.start, 200000):
            print(f"Processing {i} of 200000", end="\r")
            success = False
            while not success:
                try:
                    row = fetch_match_data(i, match_ids[i], args.platform, args.api_key)
                    writer.writerow(row)
                    success = True
                    time.sleep(args.delay)
                except Exception as e:
                    print(f"Error processing index {i}: {e}. Retrying in 120 seconds...")
                    time.sleep(120)

if __name__ == "__main__":
    main()
