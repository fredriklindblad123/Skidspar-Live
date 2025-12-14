import json
try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Verification Round 2:")
    for d in data:
        print(f"Name: {d.get('name')}")
        print(f"  URL: {d.get('url')} (Expected official URL)")
        for c in d.get('ai_comments', [])[:1]:
            print(f"  Comment Text Sample: {c.get('text')[:30]}...") 
        print("-" * 20)
except Exception as e:
    print(e)
