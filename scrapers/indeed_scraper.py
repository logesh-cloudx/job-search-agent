import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

def scrape_indeed(keywords, location="India", pages=2):
    jobs = []
    session = requests.Session()

    # First visit homepage to get cookies
    try:
        session.get('https://in.indeed.com', headers=get_headers(), timeout=10)
        time.sleep(2)
    except:
        pass

    for keyword in keywords:
        print(f"   🔍 Indeed: Searching '{keyword}'...")
        for page in range(0, pages * 10, 10):
            try:
                params = {
                    'q': keyword,
                    'l': location,
                    'start': page,
                    'fromage': '7',
                    'sort': 'date',
                    'lang': 'en'
                }
                url = "https://in.indeed.com/jobs?" + urllib.parse.urlencode(params)
                response = session.get(url, headers=get_headers(), timeout=15)

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Try multiple selectors
                job_cards = (
                    soup.find_all('div', class_='job_seen_beacon') or
                    soup.find_all('div', {'class': 'cardOutline'}) or
                    soup.find_all('div', {'data-testid': 'slider_container'}) or
                    soup.find_all('td', class_='resultContent')
                )

                for card in job_cards:
                    try:
                        title_elem = (
                            card.find('h2', class_='jobTitle') or
                            card.find('a', {'data-testid': 'job-title'}) or
                            card.find('h2')
                        )
                        company_elem = (
                            card.find('span', class_='companyName') or
                            card.find('span', {'data-testid': 'company-name'}) or
                            card.find('a', {'data-testid': 'company-name'})
                        )
                        salary_elem = (
                            card.find('div', class_='salary-snippet-container') or
                            card.find('div', class_='metadata salary-snippet-container')
                        )
                        link_elem = (
                            card.find('a', {'data-testid': 'job-title'}) or
                            card.find('a', class_='jcs-JobTitle')
                        )

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"

                        href = link_elem.get('href', '') if link_elem else ''
                        job_url = f"https://in.indeed.com{href}" if href.startswith('/') else href

                        jd_elem = card.find('div', class_='job-snippet')
                        jd = jd_elem.get_text(strip=True) if jd_elem else f"{title} at {company}"

                        jobs.append({
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": "Not specified",
                            "platform": "Indeed",
                            "url": job_url,
                            "jd": jd
                        })
                    except Exception:
                        continue

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"   ⚠️ Indeed error: {e}")
                continue

    print(f"   ✅ Indeed: Found {len(jobs)} jobs")
    return jobs