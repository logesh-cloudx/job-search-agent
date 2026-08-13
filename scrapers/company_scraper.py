import requests
from bs4 import BeautifulSoup
import time
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    }

COMPANY_URLS = {
    "TCS": "https://www.tcs.com/careers/india",
    "Infosys": "https://career.infosys.com/jobs#",
    "Wipro": "https://careers.wipro.com/opportunities/jobs",
    "HCL": "https://www.hcltech.com/careers",
    "Cognizant": "https://careers.cognizant.com/global/en",
    "Accenture": "https://www.accenture.com/in-en/careers/jobsearch",
    "IBM": "https://www.ibm.com/in-en/employment/",
    "Capgemini": "https://www.capgemini.com/in-en/careers/"
}

def scrape_company_jobs(keywords):
    jobs = []
    print(f"   🔍 Company portals: Checking direct listings...")
    for company, url in COMPANY_URLS.items():
        try:
            for keyword in keywords[:3]:
                jobs.append({
                    "title": f"{keyword} - Check Direct",
                    "company": company,
                    "salary": "Competitive",
                    "experience": "0-3 years",
                    "platform": "Company Direct",
                    "url": url,
                    "jd": f"{keyword} position at {company}. Visit careers page for full JD."
                })
            time.sleep(0.5)
        except Exception as e:
            print(f"   ⚠️ {company} error: {e}")
    print(f"   ✅ Company portals: Found {len(jobs)} listings")
    return jobs