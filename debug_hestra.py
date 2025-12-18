import requests
from bs4 import BeautifulSoup
import re

url = "https://www.skidspar.se/vastra-gotaland/boras/hestrastugan/rapporter"
print(f"Fetching {url}...")

# Use same headers/verify settings as scraper
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    response = requests.get(url, verify=False, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    text_content = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text_content.split('\n') if ln.strip()]
    
    print("\n--- Searching for '17 december' ---")
    found = False
    for i, line in enumerate(lines):
        if "17 december" in line.lower():
            found = True
            print(f"Line {i}: {line}")
            # Print neighbors
            if i+1 < len(lines): print(f"  Next: {lines[i+1]}")
            if i+2 < len(lines): print(f"  Next+1: {lines[i+2]}")

    print("\n--- Searching for 'Igår' / 'Idag' ---")
    for i, line in enumerate(lines):
        if "igår" in line.lower() or "idag" in line.lower():
            print(f"Line {i}: {line}")
            if i+1 < len(lines): print(f"  Next: {lines[i+1]}")

    print("\n--- Testing API for Hestrastugan ---")
    try:
        api_url = "https://api.skidspar.se/county/vastra-gotaland/municipalities/boras/facilities/hestrastugan"
        print(f"Fetching API: {api_url}")
        r = requests.get(api_url, verify=False, timeout=10)
        if r.status_code == 200:
            data = r.json()
            fid = data.get('id')
            print(f"Facility ID: {fid}")
            if fid:
                comments_url = f"https://api.skidspar.se/facility/{fid}/comments"
                print(f"Fetching Comments: {comments_url}")
                rc = requests.get(comments_url, verify=False, timeout=10)
                comments = rc.json()
                print(f"Found {len(comments)} comments via API.")
                for c in comments[:3]:
                    print(f"  - [{c.get('created')}] {c.get('comment')[:50]}...")
        else:
            print(f"API Error: {r.status_code}")
    except Exception as ex:
        print(f"API Exception: {ex}")

except Exception as e:
    print(f"Error: {e}")
