import json
try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Verification:")
    for d in data:
        print(f"Name: {d.get('name')}")
        print(f"  Status: {d.get('status')} (Expected 'Öppet' for Skidome)")
        print(f"  Phone: {d.get('phone')} (Expected number or '-')")
        print(f"  URL: {d.get('url')}")
        comments = d.get('ai_comments', [])
        print(f"  Comments count: {len(comments)} (Expected <= 2)")
        if comments:
             print(f"  First comment date: {comments[0].get('date')}")
        print("-" * 20)
except Exception as e:
    print(e)
