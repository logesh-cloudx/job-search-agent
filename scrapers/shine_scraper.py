import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.shine.com/',
    }

def scrape_shine(keywords, location="India", pages=2):
    """Scrape jobs from Shine.com"""
    jobs = []

    for keyword in keywords:
        print(f"   🔍 Shine: Searching '{keyword}'...")

        for page in range(1, pages + 1):
            try:
                params = {
                    'q': keyword,
                    'l': location,
                    'pg': page
                }

                url = "https://www.shine.com/job-search/" + \
                      keyword.lower().replace(' ', '-') + \
                      "-jobs?" + urllib.parse.urlencode(params)

                response = requests.get(
                    url,
                    headers=get_headers(),
                    timeout=15
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                job_cards = (
                    soup.find_all('div', class_='jobCard') or
                    soup.find_all('div', class_='job-card') or
                    soup.find_all('article', class_='job-listing')
                )

                for card in job_cards:
                    try:
                        title_elem = (
                            card.find('h2') or
                            card.find('h3') or
                            card.find('a', class_='job-title')
                        )

                        company_elem = (
                            card.find('span', class_='company-name') or
                            card.find('div', class_='company')
                        )

                        salary_elem = (
                            card.find('span', class_='salary') or
                            card.find('div', class_='salary')
                        )

                        exp_elem = (
                            card.find('span', class_='experience') or
                            card.find('div', class_='exp')
                        )

                        link_elem = card.find('a', href=True)

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) \
                            if company_elem else "Unknown"
                        salary = salary_elem.get_text(strip=True) \
                            if salary_elem else "Not specified"
                        experience = exp_elem.get_text(strip=True) \
                            if exp_elem else "Not specified"

                        href = link_elem.get('href', '') \
                            if link_elem else ''
                        if href.startswith('/'):
                            job_url = f"https://www.shine.com{href}"
                        else:
                            job_url = href

                        jd_elem = card.find('div', class_='job-desc')
                        jd = jd_elem.get_text(strip=True) \
                            if jd_elem else title

                        job = {
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": experience,
                            "platform": "Shine",
                            "url": job_url,
                            "jd": jd
                        }

                        jobs.append(job)

                    except Exception:
                        continue

                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"   ⚠️ Shine error: {e}")
                continue

    print(f"   ✅ Shine: Found {len(jobs)} jobs")
    return jobs