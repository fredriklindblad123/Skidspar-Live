import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api_url = "https://api.skidspar.se/county/vastra-gotaland/municipalities/ulricehamn/facilities/lassalyckans-skidstadion"
try:
    r = requests.get(api_url, timeout=10, verify=False)
    data = r.json()
    
    def find_key(obj, key_part):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if key_part in k.lower():
                    print(f"Found key '{k}': {v}")
                find_key(v, key_part)
        elif isinstance(obj, list):
            for i in obj:
                find_key(i, key_part)

    print("--- Searching for 'phone' ---")
    find_key(data, 'phone')
    print("--- Searching for 'tel' ---")
    find_key(data, 'tel')
    print("--- Searching for 'contact' ---")
    find_key(data, 'contact')
    
except Exception as e:
    print(f"Error: {e}")
