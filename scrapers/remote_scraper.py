import requests
from bs4 import BeautifulSoup
import time
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://remote.co/',
    }

def scrape_remote(keywords, pages=2):
    jobs = []
    for keyword in keywords:
        print(f"   🔍 Remote.co: Searching '{keyword}'...")
        try:
            keyword_url = keyword.lower().replace(' ', '-')
            url = f"https://remote.co/remote-jobs/search/?search_keywords={keyword_url}"
            response = requests.get(url, headers=get_headers(), timeout=15)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = (
                soup.find_all('div', class_='card') or
                soup.find_all('li', class_='job_listing') or
                soup.find_all('div', class_='job-listing')
            )
            for card in job_cards:
                try:
                    title_elem = card.find('h2') or card.find('h3')
                    company_elem = card.find('p', class_='company') or card.find('span', class_='company')
                    link_elem = card.find('a', href=True)
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                    href = link_elem.get('href', '') if link_elem else ''
                    job_url = f"https://remote.co{href}" if href.startswith('/') else href
                    jobs.append({
                        "title": title,
                        "company": company,
                        "salary": "Remote",
                        "experience": "Not specified",
                        "platform": "Remote.co",
                        "url": job_url,
                        "jd": title
                    })
                except Exception:
                    continue
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"   ⚠️ Remote.co error: {e}")
    print(f"   ✅ Remote.co: Found {len(jobs)} jobs")
    return jobs