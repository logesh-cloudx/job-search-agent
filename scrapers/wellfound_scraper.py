import requests
from bs4 import BeautifulSoup
import time
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://wellfound.com/',
    }

def scrape_wellfound(keywords, pages=2):
    """Scrape startup jobs from Wellfound (AngelList)"""
    jobs = []

    for keyword in keywords:
        print(f"   🔍 Wellfound: Searching '{keyword}'...")

        for page in range(1, pages + 1):
            try:
                keyword_url = keyword.lower().replace(' ', '-')
                url = f"https://wellfound.com/role/l/{keyword_url}?page={page}"

                response = requests.get(
                    url,
                    headers=get_headers(),
                    timeout=15
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                job_cards = (
                    soup.find_all('div', class_='styles_component__Ey28k') or
                    soup.find_all('div', {'data-test': 'StartupResult'}) or
                    soup.find_all('div', class_='mb-6')
                )

                for card in job_cards:
                    try:
                        title_elem = (
                            card.find('a', class_='styles_title__xpQDw') or
                            card.find('h2') or
                            card.find('span', class_='title')
                        )

                        company_elem = (
                            card.find('a', class_='styles_startup__K9BWB') or
                            card.find('span', class_='company')
                        )

                        salary_elem = card.find(
                            'span', class_='styles_compensation__3Joz5'
                        )

                        link_elem = card.find('a', href=True)

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) \
                            if company_elem else "Unknown Startup"
                        salary = salary_elem.get_text(strip=True) \
                            if salary_elem else "Not specified"

                        href = link_elem.get('href', '') \
                            if link_elem else ''
                        if href.startswith('/'):
                            job_url = f"https://wellfound.com{href}"
                        else:
                            job_url = href

                        jd_elem = card.find('div', class_='styles_description__mV2jv')
                        jd = jd_elem.get_text(strip=True) \
                            if jd_elem else title

                        job = {
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": "Not specified",
                            "platform": "Wellfound",
                            "url": job_url,
                            "jd": jd
                        }

                        jobs.append(job)

                    except Exception:
                        continue

                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"   ⚠️ Wellfound error: {e}")
                continue

    print(f"   ✅ Wellfound: Found {len(jobs)} jobs")
    return jobs