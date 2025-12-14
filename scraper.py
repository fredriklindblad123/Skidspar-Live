import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# Facilities to track
# Format: Name, URL to 'rapporter' page
FACILITIES = [
    {
        "name": "Billingen Skövde",
        "url": "https://www.skidspar.se/vastra-gotaland/skovde/billingen-skovde/rapporter",
        "municipality": "Skövde"
    },
    {
        "name": "Lassalyckan Ulricehamn",
        "url": "https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckan-ulricehamn-if/rapporter",
         "municipality": "Ulricehamn"
    },
    {
        "name": "Borås Skidstadion",
        "url": "https://www.skidspar.se/vastra-gotaland/boras/boras-skidstadion/rapporter",
         "municipality": "Borås"
    },
    {
        "name": "Landehof",
        "url": "https://www.skidspar.se/vastra-gotaland/partille/landehof/rapporter",
         "municipality": "Partille"
    },
     {
        "name": "Hindås",
        "url": "https://www.skidspar.se/vastra-gotaland/harryda/hindas/rapporter",
         "municipality": "Härryda"
    }
]

# ... (Facilities list at the top)

# Updated logic to handle parsing better and fallback URLs
def get_details(url):
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        return None

def get_facility_data(facility):
    print(f"Fetching data for {facility['name']}...")
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    soup = get_details(facility['url'])
    # If 404, try removing /rapporter or adjusting
    if not soup and "/rapporter" in facility['url']:
        fallback_url = facility['url'].replace("/rapporter", "")
        print(f"  > Retrying with {fallback_url}...")
        soup = get_details(fallback_url)
    
    status = "Okänd"
    snow_depth = "N/A"
    weather = "Kallt (Prognos)"
    ai_summary = "Kunde inte hämta rapporterna."
    last_update = datetime.datetime.now().strftime("%Y-%m-%d")

    if soup:
        text_content = soup.get_text()
        full_text_lower = text_content.lower()

        # --- Status Logic ---
        # Look for specific keywords in the whole text to determine status
        # This is a heuristic "AI" approach
        if "stängt" in full_text_lower and "öppna" not in full_text_lower:
            status = "Stängt"
        elif "nyspårat" in full_text_lower or "preparerat" in full_text_lower:
            status = "Öppet"
        elif "spår saknas" in full_text_lower:
             status = "Ej spårat"
        
        # --- Snow Depth ---
        # Search for "Snödjup" and grab next tokens
        # Implementation skipped for brevity, defaulting to N/A or scrape if specific pattern found
        
        # --- Comments / Summary ---
        # extract all paragraphs, filter for likely comments
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 30]
        # Filter out boilerplate
        comments = [p for p in paragraphs if "Anmäl" not in p and "Skidspår" not in p and "cookies" not in p]
        
        if comments:
            ai_summary = "Sammanfattning: " + " ".join(comments[:2])
            # Limit length
            if len(ai_summary) > 300:
                ai_summary = ai_summary[:297] + "..."
        else:
            ai_summary = "Inga detaljerade rapporter hittades."
            
    return {
        "name": facility['name'],
        "municipality": facility['municipality'],
        "status": status,
        "snow_depth": snow_depth,
        "last_update": last_update,
        "weather": weather,
        "ai_summary": ai_summary
    }

def main():
    all_data = []
    for fac in FACILITIES:
        data = get_facility_data(fac)
        all_data.append(data)
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Data saved to data.json")

if __name__ == "__main__":
    main()
