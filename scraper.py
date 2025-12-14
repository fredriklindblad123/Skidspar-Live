import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import random

# Facilities to track with GPS coordinates for weather data
FACILITIES = [
    {
        "name": "Billingen Skövde",
        "url": "https://www.skidspar.se/vastra-gotaland/skovde/billingen-skovde/rapporter",
        "municipality": "Skövde",
        "lat": 58.4108,
        "lon": 13.8347
    },
    {
        "name": "Lassalyckan Ulricehamn",
        "url": "https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckan-ulricehamn-if/rapporter",
        "municipality": "Ulricehamn",
        "lat": 57.7907,
        "lon": 13.4189
    },
    {
        "name": "Borås Skidstadion",
        "url": "https://www.skidspar.se/vastra-gotaland/boras/boras-skidstadion/rapporter",
        "municipality": "Borås",
        "lat": 57.7210,
        "lon": 12.9401
    },
    {
        "name": "Landehof",
        "url": "https://www.skidspar.se/vastra-gotaland/partille/landehof/rapporter",
        "municipality": "Partille",
        "lat": 57.7394,
        "lon": 12.1067
    },
    {
        "name": "Hindås",
        "url": "https://www.skidspar.se/vastra-gotaland/harryda/hindas/rapporter",
        "municipality": "Härryda",
        "lat": 57.7036372,
        "lon": 12.4460308
    }
]

def get_weather_data(lat, lon):
    """
    Hämta riktig väderdata från Open-Meteo API (gratis, ingen nyckel krävs).
    Returnerar temperatur, väderförhållande och snödjup.
    Om API:et misslyckas, returneras fallback-värden.
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,snow_depth&timezone=Europe/Stockholm"
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        temp = current.get("temperature_2m", None)
        weather_code = current.get("weather_code", None)
        snow_depth_m = current.get("snow_depth", 0) or 0
        
        # Konvertera temperatur
        temperature = f"{round(temp)}°C" if temp is not None else "Okänt"
        
        # Konvertera snödjup från meter till cm
        snow_depth_cm = round(snow_depth_m * 100)
        snow_depth = f"{snow_depth_cm} cm" if snow_depth_cm > 0 else "Ingen snö"
        
        # Konvertera WMO weather codes till svenska med emojis
        weather_descriptions = {
            0: "☀️ Klart",
            1: "🌤️ Mestadels klart",
            2: "⛅ Halvklart",
            3: "☁️ Mulet",
            45: "🌫️ Dimma",
            48: "🌫️ Rimfrost-dimma",
            51: "🌧️ Lätt duggregn",
            53: "🌧️ Duggregn",
            55: "🌧️ Kraftigt duggregn",
            61: "🌧️ Lätt regn",
            63: "🌧️ Regn",
            65: "🌧️ Kraftigt regn",
            71: "🌨️ Lätt snöfall",
            73: "❄️ Snöfall",
            75: "❄️ Kraftigt snöfall",
            77: "❄️ Snökorn",
            80: "🌧️ Lätta regnskurar",
            81: "🌧️ Regnskurar",
            82: "🌧️ Kraftiga regnskurar",
            85: "🌨️ Lätta snöbyar",
            86: "❄️ Snöbyar",
            95: "⛈️ Åskväder",
        }
        weather = weather_descriptions.get(weather_code, "☁️ Mulet")
        
        return {
            "temperature": temperature,
            "weather": weather,
            "snow_depth": snow_depth
        }
    except Exception as e:
        print(f"  > Weather API error: {e}")
        return {
            "temperature": "Okänt",
            "weather": "❓ Okänt",
            "snow_depth": "Okänt"
        }

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
    ai_summary = "Kunde inte hämta rapporterna."
    last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Hämta väderdata från Open-Meteo API
    weather_data = get_weather_data(facility.get("lat", 57.7), facility.get("lon", 12.0))
    snow_depth = weather_data["snow_depth"]
    weather = weather_data["weather"]
    temperature = weather_data["temperature"]

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
        "temperature": temperature,
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
