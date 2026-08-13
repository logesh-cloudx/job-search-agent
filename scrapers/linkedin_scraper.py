import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import urllib.parse

def scrape_linkedin(keywords, location="India", pages=3):
    """Scrape jobs from LinkedIn"""
    
    ua = fake_useragent.UserAgent()
    jobs = []
    
    for keyword in keywords:
        print(f"   🔍 LinkedIn: Searching '{keyword}'...")
        
        for page in range(0, pages * 25, 25):
            try:
                params = {
                    'keywords': keyword,
                    'location': location,
                    'start': page,
                    'f_TPR': 'r86400'  # Last 24 hours
                }
                
                url = "https://www.linkedin.com/jobs/search?" + urllib.parse.urlencode(params)
                
                headers = {
                    'User-Agent': ua.random,
                    'Accept': 'text/html',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
                
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=10
                )
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_cards = soup.find_all('div', class_='base-card')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        link_elem = card.find('a', class_='base-card__full-link')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        company = company_elem.text.strip() if company_elem else "Unknown"
                        job_url = link_elem.get('href', '') if link_elem else ''
                        
                        job = {
                            "title": title,
                            "company": company,
                            "salary": "Not specified",
                            "platform": "LinkedIn",
                            "url": job_url,
                            "jd": f"{title} at {company}"
                        }
                        
                        jobs.append(job)
                        
                    except Exception as e:
                        continue
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   ⚠️ LinkedIn error: {e}")
                continue
    
    print(f"   ✅ LinkedIn: Found {len(jobs)} jobs")
    return jobs