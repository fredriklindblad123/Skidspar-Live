import requests, urllib3
urllib3.disable_warnings()
url = "https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckan-ulricehamn/rapporter"
try:
    r = requests.get(url, timeout=15, verify=False)
    with open('lassalyckan_page.html', 'wb') as f:
        f.write(r.content)
    print('Saved', len(r.content))
except Exception as e:
    print('Error', e)
