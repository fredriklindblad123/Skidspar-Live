import json

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    targets = [f for f in data if 'Borås' in f['name'] or 'Hestra' in f['name']]
    
    for t in targets:
        print(f"\n--- {t['name']} ---")
        if t.get('ai_comments'):
            for c in t['ai_comments']:
                days_ago = c.get('days_ago', 'N/A')
                print(f"DAYS AGO: {days_ago}")
                print(f"TEXT START: {c['text'][:50]}...")
except Exception as e:
    print(e)
