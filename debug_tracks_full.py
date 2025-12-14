import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_BASE = "https://api.skidspar.se/"

def dump_tracks(url):
    parts = url.split('://')[-1].split('/', 1)[-1].split('/')
    if len(parts) >= 3:
        county, municipality, facility_slug = parts[0], parts[1], parts[2]
        u = f"{API_BASE}county/{county}/municipalities/{municipality}/facilities/{facility_slug}"
        print(f"Fetching {u}")
        r = requests.get(u, verify=False)
        data = r.json()
        
        with open('tracks_dumpjson.txt', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Dumped to tracks_dumpjson.txt")

dump_tracks("https://www.skidspar.se/vastra-gotaland/boras/boras-skidstadion/rapporter")
