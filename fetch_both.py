import requests, urllib3
urllib3.disable_warnings()
urls=[
 'https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckan-ulricehamn/rapporter',
 'https://www.skidspar.se/vastra-gotaland/ulricehamn/lassalyckan-ulricehamn-if/rapporter'
]
for u in urls:
    try:
        r=requests.get(u,timeout=15,verify=False)
        fname=('lassalyckan_if_page.html' if 'if' in u else 'lassalyckan_page.html')
        with open(fname,'wb') as f:
            f.write(r.content)
        print('Saved', fname, len(r.content))
    except Exception as e:
        print('Error', u, e)
