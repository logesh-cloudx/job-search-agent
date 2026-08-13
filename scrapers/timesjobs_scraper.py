import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.timesjobs.com/',
    }

def scrape_timesjobs(keywords, pages=2):
    jobs = []
    for keyword in keywords:
        print(f"   🔍 TimesJobs: Searching '{keyword}'...")
        for page in range(1, pages + 1):
            try:
                params = {
                    'searchType': 'personalizedSearch',
                    'from': 'submit',
                    'txtKeywords': keyword,
                    'txtLocation': '',
                    'sequence': page,
                    'startPage': page
                }
                url = "https://www.timesjobs.com/candidate/job-search.html?" + urllib.parse.urlencode(params)
                response = requests.get(url, headers=get_headers(), timeout=15)
                if response.status_code != 200:
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
                for card in job_cards:
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('h3', class_='joblist-comp-name')
                        salary_elem = card.find('li', class_='salary')
                        exp_elem = card.find('li', class_='experience')
                        link_elem = card.find('a', href=True)
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"
                        experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                        job_url = link_elem.get('href', '') if link_elem else ''
                        jd_elem = card.find('ul', class_='key-skills')
                        jd = jd_elem.get_text(strip=True) if jd_elem else title
                        jobs.append({
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": experience,
                            "platform": "TimesJobs",
                            "url": job_url,
                            "jd": jd
                        })
                    except Exception:
                        continue
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"   ⚠️ TimesJobs error: {e}")
                continue
    print(f"   ✅ TimesJobs: Found {len(jobs)} jobs")
    return jobs