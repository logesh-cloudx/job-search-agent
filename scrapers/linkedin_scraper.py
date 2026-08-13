import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def scrape_linkedin(keywords, location="India", pages=3):
    """Scrape jobs from LinkedIn without Selenium"""
    jobs = []

    session = requests.Session()

    for keyword in keywords:
        print(f"   🔍 LinkedIn: Searching '{keyword}'...")

        for page in range(0, pages * 25, 25):
            try:
                params = {
                    'keywords': keyword,
                    'location': location,
                    'start': page,
                    'f_TPR': 'r86400',
                    'f_E': '1,2',
                    'sortBy': 'DD'
                }

                url = "https://www.linkedin.com/jobs/search?" + \
                      urllib.parse.urlencode(params)

                response = session.get(
                    url,
                    headers=get_headers(),
                    timeout=15
                )

                soup = BeautifulSoup(response.text, 'html.parser')

                job_cards = (
                    soup.find_all('div', class_='base-card') or
                    soup.find_all('li', class_='jobs-search-results__list-item') or
                    soup.find_all('div', class_='job-search-card')
                )

                for card in job_cards:
                    try:
                        title_elem = (
                            card.find('h3', class_='base-search-card__title') or
                            card.find('h3') or
                            card.find('a', class_='job-card-container__link')
                        )

                        company_elem = (
                            card.find('h4', class_='base-search-card__subtitle') or
                            card.find('a', class_='hidden-nested-link') or
                            card.find('span', class_='job-card-container__company-name')
                        )

                        location_elem = (
                            card.find('span', class_='job-search-card__location') or
                            card.find('li', class_='job-card-container__metadata-item')
                        )

                        link_elem = (
                            card.find('a', class_='base-card__full-link') or
                            card.find('a', href=True)
                        )

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) \
                            if company_elem else "Unknown"
                        location = location_elem.get_text(strip=True) \
                            if location_elem else "India"

                        href = link_elem.get('href', '') \
                            if link_elem else ''

                        job = {
                            "title": title,
                            "company": company,
                            "salary": "Not specified",
                            "experience": "Not specified",
                            "platform": "LinkedIn",
                            "url": href,
                            "jd": f"{title} at {company} in {location}"
                        }

                        jobs.append(job)

                    except Exception:
                        continue

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"   ⚠️ LinkedIn error: {e}")
                continue

    print(f"   ✅ LinkedIn: Found {len(jobs)} jobs")
    return jobs