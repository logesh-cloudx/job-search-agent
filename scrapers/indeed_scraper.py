import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

def scrape_indeed(keywords, location="India", pages=2):
    """Scrape jobs from Indeed India"""
    jobs = []

    session = requests.Session()

    for keyword in keywords:
        print(f"   🔍 Indeed: Searching '{keyword}'...")

        for page in range(0, pages * 10, 10):
            try:
                params = {
                    'q': keyword,
                    'l': location,
                    'start': page,
                    'fromage': '7',  # Last 7 days
                    'sort': 'date'
                }

                url = "https://in.indeed.com/jobs?" + urllib.parse.urlencode(params)

                response = session.get(
                    url,
                    headers=get_headers(),
                    timeout=15
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Try multiple selectors
                job_cards = (
                    soup.find_all('div', class_='job_seen_beacon') or
                    soup.find_all('div', {'class': 'cardOutline'}) or
                    soup.find_all('li', class_='css-5lfssm') or
                    soup.find_all('div', {'data-testid': 'slider_container'})
                )

                for card in job_cards:
                    try:
                        # Title
                        title_elem = (
                            card.find('h2', class_='jobTitle') or
                            card.find('a', {'data-testid': 'job-title'}) or
                            card.find('span', {'title': True})
                        )

                        # Company
                        company_elem = (
                            card.find('span', class_='companyName') or
                            card.find('span', {'data-testid': 'company-name'}) or
                            card.find('a', {'data-testid': 'company-name'})
                        )

                        # Salary
                        salary_elem = (
                            card.find('div', class_='salary-snippet') or
                            card.find('div', {'data-testid': 'attribute_snippet_testid'})
                        )

                        # Link
                        link_elem = card.find('a', {'data-testid': 'job-title'})
                        if not link_elem:
                            link_elem = card.find('a', class_='jcs-JobTitle')

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"

                        if link_elem:
                            href = link_elem.get('href', '')
                            if href.startswith('/'):
                                job_url = f"https://in.indeed.com{href}"
                            else:
                                job_url = href
                        else:
                            job_url = ''

                        jd_elem = card.find('div', class_='job-snippet')
                        jd = jd_elem.get_text(strip=True) if jd_elem else title

                        job = {
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": "Not specified",
                            "platform": "Indeed",
                            "url": job_url,
                            "jd": jd
                        }

                        jobs.append(job)

                    except Exception:
                        continue

                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"   ⚠️ Indeed error: {e}")
                continue

    print(f"   ✅ Indeed: Found {len(jobs)} jobs")
    return jobs