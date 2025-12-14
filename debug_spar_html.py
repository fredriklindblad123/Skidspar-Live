
slug = "ui_ulricehamn/lassalyckans-skidstadion" # Guessing or using logic?
# The scraper uses URL parsing.
# url: https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckans-skidstadion/rapporter
# parts: vastra-gotaland, ulricehamn, lassalyckans-skidstadion

import requests
import json

api_url = "https://api.skidspar.se/county/vastra-gotaland/municipalities/ulricehamn/facilities/lassalyckans-skidstadion"
try:
    print("Fetching API:", api_url)
    r = requests.get(api_url, timeout=10, verify=False)
    data = r.json()
    with open('api_dump.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Wrote api_dump.json")
    
    # Check tracks
    if 'tracks' in data:
        print("Number of tracks:", len(data['tracks']))
        print("First track:", data['tracks'][0])

except Exception as e:
    print(f"Error: {e}")
