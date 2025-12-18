import json
import sys

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hestra = next((f for f in data if "Hestrastugan" in f['name']), None)
    if not hestra:
        print("Hestrastugan not found in data.json")
        sys.exit(1)
        
    print(f"Hestrastugan Status: {hestra.get('status')}")
    print("Comments found:")
    found_dec17 = False
    for c in hestra.get('ai_comments', []):
        text = c.get('text', '')[:60] + "..."
        print(f"  - [{c.get('date')}] {text}")
        if "17" in str(c.get('date')) or "17" in str(c.get('created', '')):
            found_dec17 = True

    if found_dec17:
        print("\n✅ Verification SUCCESS: Dec 17 comment is present locally.")
    else:
        print("\n❌ Verification FAILED: Dec 17 comment NOT found locally.")

except Exception as e:
    print(f"Error: {e}")
