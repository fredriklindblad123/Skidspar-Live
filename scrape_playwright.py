from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import datetime
import json
import re
import os

from scraper import FACILITIES

months = {
    'januari':1,'februari':2,'mars':3,'april':4,'maj':5,'juni':6,
    'juli':7,'augusti':8,'september':9,'oktober':10,'november':11,'december':12
}
date_re = re.compile(r"(\d{1,2})\s+([a-zåäö]+)\s+(\d{4})(?:\s+kl\.\s*(\d{1,2}:\d{2}))?", re.IGNORECASE)

def parse_comments_from_html(html, days_window=14):
    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text_content.split('\n') if ln.strip()]
    now = datetime.datetime.now()
    comments = []
    i = 0
    while i < len(lines):
        m = date_re.search(lines[i])
        if m:
            day = int(m.group(1))
            month_name = m.group(2).lower()
            year = int(m.group(3))
            timepart = m.group(4) or "00:00"
            month = months.get(month_name)
            # Collect following lines until next date or blank
            j = i + 1
            comment_lines = []
            while j < len(lines) and not date_re.search(lines[j]):
                comment_lines.append(lines[j])
                j += 1
            comment_text = ' '.join(comment_lines).strip()
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
                    if days_ago <= days_window:
                        comments.append({'date': dt.isoformat(), 'days_ago': days_ago, 'text': comment_text})
                except Exception:
                    pass
            i = j
        else:
            i += 1
    return comments

def slug_from_url(url):
    return url.rstrip('/').split('/')[-2] if url.rstrip('/').endswith('rapporter') else url.rstrip('/').split('/')[-1]

def main():
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        for fac in FACILITIES:
            url = fac.get('url')
            print('Rendering', fac['name'], url)
            try:
                page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception:
                try:
                    # try fallback without /rapporter
                    fallback = url.replace('/rapporter', '')
                    print('  > retrying fallback', fallback)
                    page.goto(fallback, wait_until='networkidle', timeout=30000)
                except Exception as e:
                    print('  > failed to load', e)
                    out.append({'name': fac['name'], 'url': url, 'comments': []})
                    continue

            # small wait to allow client rendering
            page.wait_for_timeout(1000)
            html = page.content()
            # save snapshot
            slug = slug_from_url(url)
            fn = f"rendered_{slug}.html"
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(html)

            comments = parse_comments_from_html(html, days_window=14)
            out.append({'name': fac['name'], 'url': url, 'comments': comments})

        browser.close()

    with open('data_playwright.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Wrote data_playwright.json')

if __name__ == '__main__':
    main()
