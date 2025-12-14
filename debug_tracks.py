import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Facility: Borås Skidstadion (or check Lassalyckan)
# URL: https://www.skidspar.se/vastra-gotaland/boras/boras-skidstadion/rapporter
# Needs ID first... handled by helper or just guess/reuse if known. 
# Let's use the code from scraper.py logic to get ID then fetch.

API_BASE = "https://api.skidspar.se/"

def inspect_tracks(url):
    print(f"Inspecting {url}...")
    parts = url.split('://')[-1].split('/', 1)[-1].split('/')
    if len(parts) >= 3:
        county, municipality, facility_slug = parts[0], parts[1], parts[2]
        u = f"{API_BASE}county/{county}/municipalities/{municipality}/facilities/{facility_slug}"
        print(f"Fetching {u}")
        r = requests.get(u, verify=False)
        data = r.json()
        
        # Dump tracks info
        if 'tracks' in data:
            print(f"Found {len(data['tracks'])} tracks.")
            for t in data['tracks']:
                print(f" - Name: {t.get('name')}")
                print(f"   Length: {t.get('length')}")
                print(f"   Status: {t.get('status')}") # Check if this exists
                print(f"   IsOpen: {t.get('isOpen')}") # Check for this
                print(f"   Groomed: {t.get('groomed')}") # Or this
                print(f"   Date: {t.get('date')}") # Last groomed?
        
        # Check if there is another endpoint for statuses? 
        # Usually /facilities/{id} has 'trackOverview' but maybe 'tracks' list is static?
        # Let's check 'trackOverview' too
        if 'trackOverview' in data:
            print("Track Overview:")
            print(json.dumps(data['trackOverview'], indent=2))

inspect_tracks("https://www.skidspar.se/vastra-gotaland/boras/boras-skidstadion/rapporter")
