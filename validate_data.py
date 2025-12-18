import json

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} facilities.")
    
    for fac in data:
        name = fac.get('name', 'UNKNOWN')
        forecast = fac.get('forecast')
        status = fac.get('status')
        temp = fac.get('temperature')
        
        missing = []
        if not forecast: missing.append("forecast")
        if not status: missing.append("status")
        if not temp or temp == "Okänt": missing.append("temperature")
        
        if missing:
            print(f"❌ {name}: MISSING {', '.join(missing)}")
        else:
            print(f"✅ {name}: OK (Status: {status}, Forecast Days: {len(forecast['dates']) if forecast else 0})")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
