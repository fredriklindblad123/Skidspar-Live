import requests
from bs4 import BeautifulSoup
import json
import html
import datetime
import re

# This is a restored scraper used only to regenerate data.json while fixing scraper.py
FACILITIES = [
    {
        "name": "Lassalyckans Skidstadion",
        "url": "https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckans-skidstadion/rapporter",
        "municipality": "Ulricehamn",
        "lat": 57.7907,
        "lon": 13.4189,
        "phone": "0321-59 59 59",
        "official_url": "https://www.ulricehamn.se/"
    },
    {
        "name": "Landvetter",
        "url": "https://www.skidspar.se/vastra-gotaland/harryda/landvetter/rapporter",
        "municipality": "Härryda",
        "lat": 57.7080,
        "lon": 12.3070,
        "phone": "-",
        "official_url": "https://oklandehof.se/"
    }
]

API_BASE = "https://api.skidspar.se/"

def get_details(url):
    try:
        r = requests.get(url, timeout=10, verify=False)
        r.raise_for_status()
        return BeautifulSoup(r.content, "html.parser")
    except Exception:
        return None


def parse_route_from_url(url):
    try:
        parts = url.split('://')[-1].split('/', 1)[-1].split('/')
        if len(parts) >= 3:
            return parts[0], parts[1], parts[2]
    except Exception:
        pass
    return None, None, None


def get_facility_api_data(facility_url):
    county, municipality, facility_slug = parse_route_from_url(facility_url)
    if not county:
        return None
    try:
        u = f"{API_BASE}county/{county}/municipalities/{municipality}/facilities/{facility_slug}"
        r = requests.get(u, timeout=10, verify=False)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def get_weather_data(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,snow_depth&timezone=Europe/Stockholm"
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        temp = current.get("temperature_2m", None)
        weather_code = current.get("weather_code", None)
        snow_depth_m = current.get("snow_depth", 0) or 0
        temperature = f"{round(temp)}°C" if temp is not None else "Okänt"
        snow_depth_cm = round(snow_depth_m * 100)
        snow_depth = f"{snow_depth_cm} cm" if snow_depth_cm > 0 else "Ingen snö"
        weather_descriptions = {0: "☀️ Klart", 1: "🌤️ Mestadels klart", 2: "⛅ Halvklart", 3: "☁️ Mulet"}
        weather = weather_descriptions.get(weather_code, "☁️ Mulet")
        return {"temperature": temperature, "weather": weather, "snow_depth": snow_depth}
    except Exception:
        return {"temperature": "Okänt", "weather": "❓ Okänt", "snow_depth": "Okänt"}


def get_facility_data(fac):
    print(f"Fetching data for {fac['name']}...")
    soup = get_details(fac['url'])
    api_data = get_facility_api_data(fac['url'])
    status = "Okänd"
    total_length = 0
    if api_data:
        overview = api_data.get('trackOverview', {})
        hours = overview.get('hoursSinceGrooming')
        num_groomed = overview.get('numGroomedTacks', 0)
        if num_groomed > 0 or (hours is not None and hours < 72):
            status = "Öppet"
        else:
            status = "Stängt"

    weather = get_weather_data(fac.get('lat'), fac.get('lon'))
    return {
        "name": fac['name'],
        "municipality": fac.get('municipality'),
        "status": status,
        "snow_depth": weather.get('snow_depth'),
        "temperature": weather.get('temperature'),
        "weather": weather.get('weather'),
        "forecast": [],
        "ai_summary": "",
        "url": fac.get('official_url') or fac['url'],
        "phone": fac.get('phone', '-'),
        "total_track_length_km": total_length,
        "ai_comments": []
    }


def main():
    out = []
    for f in FACILITIES:
        out.append(get_facility_data(f))
    with open('data.json', 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('Wrote data.json')

if __name__ == '__main__':
    main()
