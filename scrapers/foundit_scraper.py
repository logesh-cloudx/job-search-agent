import requests
import time
import random
import urllib.parse

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.foundit.in/',
    }

def scrape_foundit(keywords, pages=2):
    jobs = []
    for keyword in keywords:
        print(f"   🔍 Foundit: Searching '{keyword}'...")
        for page in range(1, pages + 1):
            try:
                params = {
                    'query': keyword,
                    'locations': '',
                    'experience': '0,3',
                    'page': page,
                    'limit': 20
                }
                url = "https://www.foundit.in/srp/results?" + urllib.parse.urlencode(params)
                response = requests.get(url, headers=get_headers(), timeout=15)
                if response.status_code != 200:
                    continue
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = (
                    soup.find_all('div', class_='jobTuple') or
                    soup.find_all('div', class_='card-apply-content') or
                    soup.find_all('div', class_='srpResultCardContainer')
                )
                for card in job_cards:
                    try:
                        title_elem = card.find('h2') or card.find('a', class_='title')
                        company_elem = card.find('span', class_='company') or card.find('a', class_='company')
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
                        job_url = f"https://www.foundit.in{href}" if href.startswith('/') else href
                        jobs.append({
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": experience,
                            "platform": "Foundit",
                            "url": job_url,
                            "jd": title
                        })
                    except Exception:
                        continue
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"   ⚠️ Foundit error: {e}")
                continue
    print(f"   ✅ Foundit: Found {len(jobs)} jobs")
    return jobs