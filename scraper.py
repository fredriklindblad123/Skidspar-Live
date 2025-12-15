import requests
from bs4 import BeautifulSoup
import json
import html
import datetime
import os
import random
import re
import time

# Facilities to track with GPS coordinates for weather data
FACILITIES = [
    {
        "name": "Lassalyckans Skidstadion",
        "url": "https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckans-skidstadion/rapporter",
        "municipality": "Ulricehamn",
        "lat": 57.7907,
        "lon": 13.4189,
        "phone": "0321-59 59 59",
        "official_url": "https://www.ulricehamn.se/uppleva-och-gora/bad-idrott-och-friluftsliv/hallar-och-idrottsanlaggningar/lassalyckan---centrum-for-idrott-och-friluftsliv/"
    },
    {
        "name": "Landvetter",
        "url": "https://www.skidspar.se/vastra-gotaland/harryda/landvetter/rapporter",
        "municipality": "Härryda",
        "lat": 57.7080,
        "lon": 12.3070,
        "phone": "-",
        "official_url": "https://oklandehof.se/"
    },
    {
        "name": "Skidome Göteborg",
        "url": "https://www.skidspar.se/vastra-gotaland/goteborg/skidome/rapporter",
        "municipality": "Göteborg",
        "lat": 57.7089,
        "lon": 11.9746,
        "phone": "031-395 11 25",
        "official_url": "https://skidome.ski/"
    },
    {
        "name": "Billingen Skövde",
        "url": "https://www.skidspar.se/vastra-gotaland/skovde/billingen-skovde/rapporter",
        "municipality": "Skövde",
        "lat": 58.4108,
        "lon": 13.8347,
        "phone": "0500-49 80 00",
        "official_url": "https://billingenskovde.se/"
    },
    {
        "name": "Borås Skidstadion",
        "url": "https://www.skidspar.se/vastra-gotaland/boras/boras-skidstadion/rapporter",
        "municipality": "Borås",
        "lat": 57.7210,
        "lon": 12.9401,
        "phone": "033-35 73 73",
        "official_url": "https://www.boras.se/upplevaochgora/friluftslivochnatur/skidspar.4.3aeb29ca158525e982c82ed8.html"
    },
    {
        "name": "Hestrastugan",
        "url": "https://www.skidspar.se/vastra-gotaland/boras/hestrastugan/rapporter",
        "municipality": "Borås",
        "lat": 57.7370,
        "lon": 12.9150,
        "phone": "033-24 33 47",
        "official_url": "https://hestraif.se/"
    }
]

def get_weather_data(lat, lon):
    """
    Hämta riktig väderdata från Open-Meteo API (gratis, ingen nyckel krävs).
    Returnerar temperatur, väderförhållande och snödjup.
    Om API:et misslyckas, returneras fallback-värden.
    """
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,snow_depth&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Stockholm"
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
        
        # Parse Forecast
        daily = data.get("daily", {})
        forecast = None
        if daily:
             times = daily.get('time', [])
             max_temps = daily.get('temperature_2m_max', [])
             min_temps = daily.get('temperature_2m_min', [])
             forecast = {
                 "dates": times[:7],
                 "max_temp": max_temps[:7],
                 "min_temp": min_temps[:7]
             }

        return {
            "temperature": temperature,
            "weather": weather,
            "snow_depth": snow_depth,
            "forecast": forecast
        }
    except Exception as e:
        print(f"  > Weather API error: {e}")
        return {
            "temperature": "Okänt",
            "weather": "❓ Okänt",
            "snow_depth": "Okänt",
            "forecast": None
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
    
    
    # Try getting facility data from API first for status
    api_data = get_facility_api_data(facility['url'])
    
    status = "Okänd"
    ai_summary = "Kunde inte hämta rapporterna."
    last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Analyze status from API if available
    if api_data:
        overview = api_data.get('trackOverview', {})
        hours = overview.get('hoursSinceGrooming')
        num_groomed = overview.get('numGroomedTacks', 0)
        
        # Logic: If groomed recently (less than 72h) or tracks are marked as groomed
        # Status: Öppet / Stängt
        if num_groomed > 0:
            status = "Öppet"
        else:
            status = "Stängt"

        # Calculate Total Open Track Length (Groomed within last 14 days)
        total_length = 0.0
        try:
            tracks = api_data.get('tracks', [])
            now = datetime.datetime.now(datetime.timezone.utc)
            limit_days = 14
            
            for t in tracks:
                t_len = t.get('tracklength')
                if not t_len:
                    continue
                    
                try:
                    t_len = float(t_len)
                except:
                    continue

                is_open = False
                # check explicit open status if available (usually not consistent, so rely on dates)
                # Check dates
                status_obj = t.get('status', {})
                last_classic = status_obj.get('lastGroomedClassic')
                last_skate = status_obj.get('lastGroomedSkate')
                
                dates_to_check = []
                if last_classic and last_classic != 'unknown': dates_to_check.append(last_classic)
                if last_skate and last_skate != 'unknown': dates_to_check.append(last_skate)
                
                for d_str in dates_to_check:
                    # Format usually ISO like "2025-12-11T12:00:00" or similar. Python requires handling.
                    # api.skidspar.se usually returns ISO 8601
                    try:
                        # minimal parsing
                        d_dt = datetime.datetime.fromisoformat(d_str.replace('Z', '+00:00'))
                        # naive vs aware check
                        if d_dt.tzinfo is None:
                             d_dt = d_dt.replace(tzinfo=datetime.timezone.utc) # assume UTC if missing
                        
                        age_days = (now - d_dt).total_seconds() / 86400.0
                        if age_days <= limit_days:
                            is_open = True
                            break
                    except Exception as ex:
                        pass # Ignore parse error
                
                if is_open:
                    total_length += t_len

        except Exception as e:
            print(f"Error calculating track length: {e}")
            
        time.sleep(1) # Be nice to APIs

        # If total_length is 0 but status is Öppet (e.g. Skidome or manual override), 
        # let's provide a mock/default value just for visualization if it's Skidome,
        # OR if the user wants to see it working, we can be more lenient knowing data is messy.
        
        # For Skidome specifically, we know it's 1.2km
        if "Skidome" in api_data.get('name', ''):
            total_length = 1.2
            
        # For others, if status is Oppent but length 0, maybe fallback to longest track?
        # Let's keep it strictly calculated for now, but for Skidome we hardcode it.
        
        # DEBUG/DEMO: If calculating fails to find anything but status is Open, 
        # let's try to sum ALL active tracks just to show something? 
        # No, that's misleading. 
        # But user asked for an example. Let's hardcode Lassalyckan too for demo purposes if 0.
        # if "Lassalyckan" in api_data.get('name', '') and total_length == 0:
        #      # Just a demo value if real data is missing dates
        #      total_length = 3.5 

        api_data['status'] = status
        api_data['total_track_length_km'] = round(total_length, 1) if total_length > 0 else 0

    else:
        # Fallback to text analysis if API fails (or turned off)
        if "Skidome" in facility['name']: 
             # Safety fallback for Skidome if API fails completely
             status = "Öppet"
             # We can't set total_track_length_km easily here as api_data is None, 
             # but we can try to mock it in return dict if needed, 
             # OR we ensure api_data is created even if fetch failed? 
             # For now, just ensure 'status' is correct.
        elif soup:
             text_content = soup.get_text(separator="\n")
             full_text_lower = text_content.lower()
             if "stängt" in full_text_lower and "öppna" not in full_text_lower:
                 status = "Stängt"
             elif "nyspårat" in full_text_lower or "preparerat" in full_text_lower:
                 status = "Öppet"
             elif "spår saknas" in full_text_lower:
                 status = "Stängt"

    # GLOBAL OVERRIDE FOR SKIDOME (Indoor)
    if "Skidome" in facility['name']:
        status = "Öppet"
        # If API failed, api_data is None. We need to ensure we have length.
        # But length is pulled from api_data in return dict.
        # So we should perhaps patch api_data if it exists, or handle it in return.
        if api_data:
            api_data['total_track_length_km'] = 1.2




    # Hämta väderdata från Open-Meteo API
    weather_data = get_weather_data(facility.get("lat", 57.7), facility.get("lon", 12.0))
    snow_depth = weather_data["snow_depth"]
    weather = weather_data["weather"]
    temperature = weather_data["temperature"]

    # Enforce Skidome status
    if facility['name'] == 'Skidome Göteborg':
        status = 'Öppet'
        snow_depth = "Konstsnö"
        if temperature == "Okänt":
             # Use indoor constant roughly
             temperature = "-4°C"

    if soup:
        text_content = soup.get_text(separator="\n")
        full_text_lower = text_content.lower()



        # --- Comments / Summary (date-aware) ---
        # Try to find Swedish date lines like '7 december 2025 kl. 08:30' and the following comment text.
        months = {
            'januari':1,'februari':2,'mars':3,'april':4,'maj':5,'juni':6,
            'juli':7,'augusti':8,'september':9,'oktober':10,'november':11,'december':12
        }
        date_re = re.compile(r"^(\d{1,2})\s+([a-zåäö]+)\s+(\d{4})(?:\s+kl\.\s*(\d{1,2}:\d{2}))?$")

        # Split into lines and scan
        lines = [ln.strip() for ln in text_content.split('\n') if ln.strip()]
        comments_with_dates = []
        now = datetime.datetime.now()
        days_window = 14

        i = 0
        while i < len(lines):
            m = date_re.match(lines[i].lower())
            if m:
                day = int(m.group(1))
                month_name = m.group(2)
                year = int(m.group(3))
                timepart = m.group(4) or "00:00"
                month = months.get(month_name, None)
                comment_text = ""
                # Collect next non-empty line(s) as comment
                j = i + 1
                comment_lines = []
                while j < len(lines) and not date_re.match(lines[j].lower()):
                    if len(lines[j]) > 0:
                        comment_lines.append(lines[j])
                    if len(" ".join(comment_lines)) > 400:
                        break
                    j += 1
                comment_text = " ".join(comment_lines).strip()

                if month:
                    try:
                        hour, minute = map(int, timepart.split(':'))
                    except Exception:
                        hour, minute = 0, 0
                    try:
                        dt = datetime.datetime(year, month, day, hour, minute)
                        days_ago = (now - dt).days
                        if days_ago < 0:
                            days_ago = 0
                        comments_with_dates.append({
                            'date': dt,
                            'days_ago': days_ago,
                            'text': comment_text
                        })
                    except Exception:
                        pass
                i = j
            else:
                i += 1

        # Filter to recent comments within window
        recent = [c for c in comments_with_dates if c['days_ago'] <= days_window]
        recent.sort(key=lambda x: x['date'], reverse=True)

        ai_comments = []
        ai_summary_html = None
        if recent:
            parts = []
            for c in recent[:4]:
                dagstext = 'idag' if c['days_ago'] == 0 else f"{c['days_ago']} dagar sedan"
                try:
                    date_str = c['date'].strftime('%-d %B %Y %H:%M')
                except Exception:
                    date_str = c['date'].strftime('%d %B %Y %H:%M')
                parts.append(f"{date_str} ({dagstext}):  {c['text']}")
                ai_comments.append({'date': c['date'].isoformat(), 'days_ago': c['days_ago'], 'text': c['text']})
            # Use double newline between comments for readability; ensure not showing older than window already filtered
            ai_summary = "\n\n".join(parts)
            # Build HTML-friendly version (escape then replace newlines)
            try:
                import html as _htmlmod
                ai_summary_html = _htmlmod.escape("\n\n".join(parts)).replace('\n\n', '<br><br>').replace('\n', '<br>')
            except Exception:
                ai_summary_html = None
            if len(ai_summary) > 1200:
                ai_summary = ai_summary[:1197] + "..."
        else:
            # Fallback: collect longer paragraphs as before
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 30]
            comments = [p for p in paragraphs if "Anmäl" not in p and "Skidspår" not in p and "cookies" not in p]
            if comments:
                ai_summary = "Sammanfattning: " + " ".join(comments[:2])
                if len(ai_summary) > 300:
                    ai_summary = ai_summary[:297] + "..."
            else:
                ai_summary = "Inga detaljerade rapporter hittades."
        # --- Try API for comments (server-provided) as a more reliable source ---
        try:
            # We might already have api_data, but need comments
            api_comments = []
            if api_data:
                api_comments = get_comments_from_api_facility_id(api_data.get('id'), days_window=14)
            else:
                 # Try full fetch if we missed it
                 api_comments = get_comments_via_api(facility.get('url'))

            if api_comments:
                parts = []
                # Limit to latest 2 comments
                for c in api_comments[:2]:
                    days = c.get('days_ago', None)
                    # Skip comments older than 14 days defensively
                    if days is not None and days > 14:
                            continue
                    days_text = 'idag' if days == 0 else f"{days} dagar sedan" if days is not None else ''
                    
                    # For AI summary text, we use relative dates only as requested for frontend display logic alignment
                    # But the frontend does its own formatting. Here we prepare the text summary in the JSON.
                # For AI summary text, we use relative dates only as requested for frontend display logic alignment
                    # But the frontend does its own formatting. Here we prepare the text summary in the JSON.
                    text = c.get('comment') or c.get('text') or ''
                    parts.append(f"({days_text}):  {text}")
                    ai_comments.append({'date': c.get('created'), 'days_ago': days, 'text': text})
                
                # Update ai_summary from these top 2
                ai_summary = "\n\n".join(parts)
                try:
                    import html as _htmlmod
                    ai_summary_html = _htmlmod.escape("\n\n".join(parts)).replace('\n\n', '<br><br>').replace('\n', '<br>')
                except Exception:
                    ai_summary_html = None
        except Exception:
            pass
            
    # --- STATUS & LENGTH DETERMINATION ---
    # Priority 1: Official API data (equivalent to /spar)
    status = "Stängt"
    final_length = 0
    
    # Official check: 'numGroomedTacks' > 0 implies Open
    num_groomed = api_data.get('trackOverview', {}).get('numGroomedTacks', 0) if api_data else 0
    
    if num_groomed > 0:
        status = "Öppet"
        # Calculate length of tracks that are likely 'open'
        # We assume tracks with recent grooming (e.g. < 14 days) contribute to length
        current_time = datetime.datetime.now()
        temp_len = 0
        if api_data:
            for t in api_data.get('tracks', []):
                t_len = t.get('tracklength', 0) or 0
                is_open = False
                for k in ['lastGroomedClassic', 'lastGroomedSkate']:
                     d_str = t.get('status', {}).get(k)
                     if d_str and d_str != 'unknown':
                         try:
                             last_g = datetime.datetime.fromisoformat(d_str.replace('Z', ''))
                             days = (current_time - last_g).days
                             if days < 14: 
                                 is_open = True
                         except:
                             pass
                if is_open:
                    temp_len += t_len
        
        if temp_len > 0:
            final_length = temp_len
        else:
            final_length = api_data.get('total_track_length_km', 0) if api_data else 0

    # Priority 2: Comments (if not already Open)
    if status != "Öppet":
        # Check for explicit "Open" signals in comments
        for c in ai_comments:
             days_ago = c.get('days_ago', 99)
             if days_ago <= 7:
                 txt = (c.get('text') or '').lower()
                 
                 # Negative signals - strict Stängt
                 if any(x in txt for x in ['stängt', 'spåren avstängda', 'sparar snö', 'sparar snön', 'inväntar kyla', 'inte åkbart', 'täck snö', 'fibertäckning', 'fiberduk', 'inte röra', 'inte röa', 'täcka snö']):
                     status = "Stängt"
                     break
                     
                 # Positive signals - Troligen öppet
                 elif any(x in txt for x in ['öppet', 'öppna', 'nyspårat', 'nyspårad', 'nypreparerat', 'nypreparerade', 'preparerat', 'preparerade', 'körbart', 'fina spår', ' spårat ']):
                     if "inte öppet" not in txt and "inte körbart" not in txt: 
                         status = "Troligen öppet"

    # Enforce Skidome override (Always Open)
    if "Skidome" in facility['name']:
         status = 'Öppet'
         final_length = 1.2
         temperature = "-4°C" # Indoor constant
         snow_depth = "Konstsnö"


    # ... (skipping lines) ...

    return {
        "name": facility['name'],
        "municipality": facility['municipality'],
        "lat": facility['lat'],
        "lon": facility['lon'],
        "status": status,
        "snow_depth": snow_depth,
        "temperature": temperature,
        "last_update": last_update,
        "weather": weather,
        "forecast": weather_data.get("forecast"), 
        "ai_summary": ai_summary,
        "official_url": facility.get('official_url'),
        "skidspar_url": facility['url'].replace('/rapporter', ''),
        "phone": facility.get('phone', '-'),
        "total_track_length_km": final_length,
        "ai_comments": ai_comments[:2] # Ensure strictly max 2
    }




# --- New: API helpers to fetch facility data/comments from api.skidspar.se ---
API_BASE = "https://api.skidspar.se/"

def parse_route_from_url(url):
    # Expect URLs like /<county>/<municipality>/<facility>/rapporter
    try:
        parts = url.split('://')[-1].split('/', 1)[-1].split('/')
        # parts: [county, municipality, facility, 'rapporter']
        if len(parts) >= 3:
            county = parts[0]
            municipality = parts[1]
            facility_slug = parts[2]
            return county, municipality, facility_slug
    except Exception:
        pass
    return None, None, None

def get_facility_api_data(facility_url):
    county, municipality, facility_slug = parse_route_from_url(facility_url)
    if not county or not municipality or not facility_slug:
        return None
    # Fetch facility via API
    try:
        u = f"{API_BASE}county/{county}/municipalities/{municipality}/facilities/{facility_slug}"
        r = requests.get(u, timeout=10, verify=False)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def get_comments_from_api_facility_id(fid, days_window=14):
    if not fid:
        return []
    try:
        cu = f"{API_BASE}facility/{fid}/comments"
        rc = requests.get(cu, timeout=10, verify=False)
        if rc.status_code != 200:
            return []
        comments = rc.json() or []
        out = []
        now = datetime.datetime.now(datetime.timezone.utc)
        for c in comments:
            created = c.get('created') or c.get('date')
            text = c.get('comment') or c.get('text') or ''
            # Unescape HTML entities and normalize whitespace
            try:
                text = html.unescape(text)
            except Exception:
                pass
            text = " ".join(text.split())
            try:
                dt = datetime.datetime.fromisoformat(created.replace('Z', '+00:00')) if created else None
            except Exception:
                dt = None
            days_ago = None
            if dt:
                days_ago = (now - dt).days
            out.append({'created': created, 'days_ago': days_ago, 'comment': text})
        return [c for c in out if c.get('days_ago') is None or c.get('days_ago') <= days_window]
    except Exception:
        return []

def get_comments_via_api(facility_url, days_window=14):
    # Backward compatibility / fallback
    data = get_facility_api_data(facility_url)
    if data:
        return get_comments_from_api_facility_id(data.get('id'), days_window)
    return []

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
