import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://www.hirist.tech/',
    }

def scrape_hirist(keywords, pages=2):
    jobs = []
    for keyword in keywords:
        print(f"   🔍 Hirist: Searching '{keyword}'...")
        for page in range(1, pages + 1):
            try:
                params = {'q': keyword, 'page': page}
                url = "https://www.hirist.tech/search?" + urllib.parse.urlencode(params)
                response = requests.get(url, headers=get_headers(), timeout=15)
                if response.status_code != 200:
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = (
                    soup.find_all('div', class_='job-card') or
                    soup.find_all('li', class_='job-listing') or
                    soup.find_all('div', class_='listing-container')
                )
                for card in job_cards:
                    try:
                        title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='title')
                        company_elem = card.find('span', class_='company-name') or card.find('div', class_='company')
                        salary_elem = card.find('span', class_='salary')
                        exp_elem = card.find('span', class_='experience')
                        link_elem = card.find('a', href=True)
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"
                        experience = exp_elem.get_text(strip=True) if exp_elem else "Not specified"
                        href = link_elem.get('href', '') if link_elem else ''
                        job_url = f"https://www.hirist.tech{href}" if href.startswith('/') else href
                        jobs.append({
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": experience,
                            "platform": "Hirist",
                            "url": job_url,
                            "jd": title
                        })
                    except Exception:
                        continue
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"   ⚠️ Hirist error: {e}")
    print(f"   ✅ Hirist: Found {len(jobs)} jobs")
    return jobs