import json
import csv
import time
import argparse
from urllib.request import urlopen
from urllib.error import HTTPError

def fetch_match_ids(j, puuid, platform, api_key):
    url = f"https://{platform}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={api_key}"
    response = urlopen(url)
    data = json.loads(response.read())
    data.insert(0,j)
    return data

def main():
    parser = argparse.ArgumentParser(description="Scrape match IDs from PUUIDs.")
    parser.add_argument("--api_key", required=True, help="Riot Games API key.")
    parser.add_argument("--platform", required=True, help="Platform for API requests (e.g., americas, europe).")
    parser.add_argument("--input", required=True, help="Path to the input PUUID CSV file.")
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    parser.add_argument("--delay", required=True, help="Delay to match Riot Games API (hint: start with 1.2 and titrate down).")
    parser.add_argument("--start", required=True, help="Scraping may pause abruptly. Start with 0 if beginning to scrape; otherwise, input the index number from previous attempt.")
    
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        puuids = {row[i] for row in csv.reader(f) for i in range(1, 11)}

    with open(args.output, 'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        for i in range(args.start, len(puuids)):
            print(f"Processing {i} of {len(puuids)}", end="\r")
            success = False
            while not success:
                try:
                    match_ids = fetch_match_ids(i, puuids[i], args.platform, args.api_key)
                    writer.writerow(match_ids)
                    success = True
                    time.sleep(args.delay)
                except HTTPError as e:
                    print(f"\nError fetching match IDs index {i}: {e} \n Trying again in 2 minutes...")
                    time.sleep(120)


if __name__ == "__main__":
    main()
