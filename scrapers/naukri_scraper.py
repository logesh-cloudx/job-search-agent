import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.naukri.com/',
        'appid': '109',
        'systemid': '109',
    }

def scrape_naukri(keywords, location="India", pages=2):
    """Scrape jobs from Naukri using their API"""
    jobs = []
    session = requests.Session()

    # Warm up session cookies before hitting the API
    try:
        session.get('https://www.naukri.com/', headers=get_headers(), timeout=10)
        time.sleep(1)
    except Exception:
        pass

    for keyword in keywords:
        print(f"   🔍 Naukri: Searching '{keyword}'...")

        for page in range(1, pages + 1):
            try:
                params = {
                    'noOfResults': 20,
                    'urlType': 'search_by_keyword',
                    'searchType': 'adv',
                    'keyword': keyword,
                    'pageNo': page,
                    'k': keyword,
                    'l': '',
                    'seoKey': keyword.lower().replace(' ', '-'),
                    'src': 'jobsearchDesk',
                    'latLong': ''
                }

                url = "https://www.naukri.com/jobapi/v3/search?" + urllib.parse.urlencode(params)

                response = session.get(
                    url,
                    headers=get_headers(),
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    job_list = data.get('jobDetails', [])

                    for item in job_list:
                        try:
                            # Get salary
                            salary_info = item.get('placeholders', [])
                            salary = "Not specified"
                            for p in salary_info:
                                if p.get('type') == 'salary':
                                    salary = p.get('label', 'Not specified')
                                    break

                            # Get experience
                            exp = "Not specified"
                            for p in salary_info:
                                if p.get('type') == 'experience':
                                    exp = p.get('label', 'Not specified')
                                    break

                            job = {
                                "title": item.get('title', 'Unknown'),
                                "company": item.get('companyName', 'Unknown'),
                                "salary": salary,
                                "experience": exp,
                                "platform": "Naukri",
                                "url": item.get('jdURL', ''),
                                "jd": item.get('jobDescription', item.get('title', ''))
                            }
                            jobs.append(job)

                        except Exception as e:
                            continue

                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"   ⚠️ Naukri error: {e}")
                continue

    print(f"   ✅ Naukri: Found {len(jobs)} jobs")
    return jobs