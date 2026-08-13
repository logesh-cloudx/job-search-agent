import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.glassdoor.co.in/',
    }

def scrape_glassdoor(keywords, location="India", pages=2):
    """Scrape jobs from Glassdoor India"""
    jobs = []

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
                    'minSalary': '0',
                    'includeNoSalaryJobs': 'true',
                    'radius': '100',
                    'cityId': '-1',
                    'minRating': '0.0',
                    'industryId': '-1',
                    'sgocId': '-1',
                    'seniorityType': 'entry',
                    'companyId': '-1',
                    'enabledFacets[]': ['JOB_FUNCTIONS'],
                    'p': page
                }

                url = "https://www.glassdoor.co.in/Job/jobs.htm?" + \
                      urllib.parse.urlencode(params)

                response = requests.get(
                    url,
                    headers=get_headers(),
                    timeout=15
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                job_cards = (
                    soup.find_all('li', class_='react-job-listing') or
                    soup.find_all('div', class_='jobCard') or
                    soup.find_all('article', {'data-test': 'jobListing'})
                )

                for card in job_cards:
                    try:
                        title_elem = (
                            card.find('a', class_='jobLink') or
                            card.find('a', {'data-test': 'job-link'}) or
                            card.find('span', {'data-test': 'job-title'})
                        )

                        company_elem = (
                            card.find('div', class_='jobHeader') or
                            card.find('span', class_='css-63koeb')
                        )

                        salary_elem = (
                            card.find('span', class_='css-1xe2xww') or
                            card.find('div', {'data-test': 'detailSalary'})
                        )

                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) \
                            if company_elem else "Unknown"
                        salary = salary_elem.get_text(strip=True) \
                            if salary_elem else "Not specified"

                        href = title_elem.get('href', '') \
                            if hasattr(title_elem, 'get') else ''
                        if href.startswith('/'):
                            job_url = f"https://www.glassdoor.co.in{href}"
                        else:
                            job_url = href

                        jd_elem = card.find('div', class_='jobDescriptionContent')
                        jd = jd_elem.get_text(strip=True) \
                            if jd_elem else title

                        job = {
                            "title": title,
                            "company": company,
                            "salary": salary,
                            "experience": "Not specified",
                            "platform": "Glassdoor",
                            "url": job_url,
                            "jd": jd
                        }

                        jobs.append(job)

                    except Exception:
                        continue

                time.sleep(random.uniform(2, 3))

            except Exception as e:
                print(f"   ⚠️ Glassdoor error: {e}")
                continue

    print(f"   ✅ Glassdoor: Found {len(jobs)} jobs")
    return jobs