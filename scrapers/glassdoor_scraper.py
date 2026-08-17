import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random
import json

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.glassdoor.co.in/',
    }

def scrape_glassdoor(keywords, pages=2):
    jobs = []
    session = requests.Session()

    try:
        session.get('https://www.glassdoor.co.in', headers=get_headers(), timeout=10)
        time.sleep(2)
    except:
        pass

    for keyword in keywords:
        print(f"   🔍 Glassdoor: Searching '{keyword}'...")
        for page in range(1, pages + 1):
            try:
                params = {
                    'sc.keyword': keyword,
                    'locT': 'N',
                    'locId': '115',
                    'jobType': '',
                    'fromAge': '7',
                    'p': page
                }
                url = "https://www.glassdoor.co.in/Job/jobs.htm?" + urllib.parse.urlencode(params)
                response = session.get(url, headers=get_headers(), timeout=15)

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # Try JSON data embedded in page
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, list):
                            for item in data:
                                if item.get('@type') == 'JobPosting':
                                    jobs.append({
                                        "title": item.get('title', 'Unknown'),
                                        "company": item.get('hiringOrganization', {}).get('name', 'Unknown'),
                                        "salary": "Not specified",
                                        "experience": "Not specified",
                                        "platform": "Glassdoor",
                                        "url": item.get('url', ''),
                                        "jd": item.get('description', '')[:500]
                                    })
                    except:
                        continue

                # Also try HTML parsing
                job_cards = (
                    soup.find_all('li', {'data-test': 'jobListing'}) or
                    soup.find_all('article', class_='jobCard') or
                    soup.find_all('div', class_='react-job-listing')
                )

                for card in job_cards:
                    try:
                        title_elem = card.find('a', {'data-test': 'job-title'}) or card.find('h2')
                        company_elem = card.find('span', {'data-test': 'employer-name'})
                        link_elem = card.find('a', href=True)

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        href = link_elem.get('href', '') if link_elem else ''
                        job_url = f"https://www.glassdoor.co.in{href}" if href.startswith('/') else href

                        jobs.append({
                            "title": title,
                            "company": company,
                            "salary": "Not specified",
                            "experience": "Not specified",
                            "platform": "Glassdoor",
                            "url": job_url,
                            "jd": f"{title} at {company}"
                        })
                    except:
                        continue

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"   ⚠️ Glassdoor error: {e}")
                continue

    print(f"   ✅ Glassdoor: Found {len(jobs)} jobs")
    return jobs