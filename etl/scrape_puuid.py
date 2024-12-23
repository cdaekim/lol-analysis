import json
import csv
import time
import argparse
from urllib.request import urlopen
from urllib.error import HTTPError

def fetch_puuid(j, match_id, platform, api_key, region):
    url = f"https://{platform}.api.riotgames.com/lol/match/v5/matches/{region}_{match_id}?api_key={api_key}"
    response = urlopen(url)
    data = json.loads(response.read())
    return [j+data['info']['participants'][i]['puuid'] for i in range(10)]

def main():
    parser = argparse.ArgumentParser(description="Scrape PUUIDs from match IDs.")
    parser.add_argument("--api_key", required=True, help="Riot Games API key.")
    parser.add_argument("--region", required=True, help="Region for match data (e.g., NA1, EUW1).")
    parser.add_argument("--platform", required=True, help="Platform for API requests (e.g., americas, europe).")
    parser.add_argument("--input", required=True, help="Path to the input matchlist JSON file.")
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    parser.add_argument("--delay", required=True, help="Delay to match Riot Games API (hint: start with 1.2 and titrate down).")
    parser.add_argument("--start", required=True, help="Scraping may pause abruptly. Start with 0 if beginning to scrape; otherwise, input the index number from previous attempt.")
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        matchlist = json.load(f)

    with open(args.output, 'a+', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for i in range(args.start, len(matchlist)):
            print(f"Processing match {i}", end="\r")
            success = False
            while not success:
                try:
                    puuids = fetch_puuid(i, args.platform, args.api_key, args.region)
                    writer.writerow(puuids)
                    success = True
                    time.sleep(args.delay)
                except HTTPError as e:
                    print(f"\nError fetching match {i}: {e} \n Trying again in 2 minutes.")
                    time.sleep(120)

    
if __name__ == "__main__":
    main()
