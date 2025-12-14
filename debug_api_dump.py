# Cleanup old file
import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_url = "https://api.skidspar.se/county/vastra-gotaland/municipalities/ulricehamn/facilities/lassalyckans-skidstadion"
try:
    print("Fetching API:", api_url)
    r = requests.get(api_url, timeout=10, verify=False)
    data = r.json()
    # Check for phone or contact info recursivley
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
