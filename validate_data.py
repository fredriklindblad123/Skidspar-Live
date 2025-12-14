import json
try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Statuses:")
    for d in data:
        print(f"{d.get('name')}: {d.get('status')} (Groomed: {d.get('snow_depth')}, Weather: {d.get('weather')})")
except Exception as e:
    print(e)
