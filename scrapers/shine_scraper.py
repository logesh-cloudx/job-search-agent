import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random
import json

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.shine.com/',
    }

def scrape_shine(keywords, pages=2):
    jobs = []
    session = requests.Session()

    try:
        session.get('https://www.shine.com', headers=get_headers(), timeout=10)
        time.sleep(1)
    except:
        pass

    for keyword in keywords:
        print(f"   🔍 Shine: Searching '{keyword}'...")
        for page in range(1, pages + 1):
            try:
                keyword_url = keyword.lower().replace(' ', '-')
                url = f"https://www.shine.com/job-search/{keyword_url}-jobs"

                params = {'q': keyword, 'pg': page}
                url = f"{url}?{urllib.parse.urlencode(params)}"

                response = session.get(url, headers=get_headers(), timeout=15)

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Shine is a Next.js app - job data ships as embedded JSON,
                # not stable HTML/CSS class names.
                next_data = soup.find('script', id='__NEXT_DATA__')
                if not next_data or not next_data.string:
                    continue

                data = json.loads(next_data.string)
                results = (
                    data.get('props', {})
                        .get('pageProps', {})
                        .get('initialState', {})
                        .get('jsrp', {})
                        .get('searchresult', {})
                        .get('data', {})
                        .get('results', [])
                )

                for item in results:
                    try:
                        title = item.get('jJT', 'Unknown')
                        company = item.get('jCName', 'Unknown')
                        salary = item.get('jSal') or "Not specified"
                        experience = item.get('jExp') or "Not specified"
                        jd_html = item.get('jJD', '')
                        jd = BeautifulSoup(jd_html, 'html.parser').get_text(' ', strip=True) if jd_html else title
                        slug = item.get('jSlug', '')
                        job_url = f"https://www.shine.com/jobs/{slug}" if slug else ''

                        jobs.append({
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": experience,
                            "platform": "Shine",
                            "url": job_url,
                            "jd": jd
                        })
                    except:
                        continue

                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"   ⚠️ Shine error: {e}")
                continue

    print(f"   ✅ Shine: Found {len(jobs)} jobs")
    return jobs