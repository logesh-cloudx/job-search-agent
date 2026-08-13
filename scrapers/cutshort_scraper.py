import requests
import time
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Referer': 'https://cutshort.io/',
    }

def scrape_cutshort(keywords):
    jobs = []
    for keyword in keywords:
        print(f"   🔍 Cutshort: Searching '{keyword}'...")
        try:
            payload = {
                "query": keyword,
                "locations": [],
                "experience": {"min": 0, "max": 3},
                "skip": 0,
                "limit": 20
            }
            url = "https://cutshort.io/api/v6/jobs/search"
            response = requests.post(
                url,
                json=payload,
                headers=get_headers(),
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                job_list = data.get('data', [])
                for item in job_list:
                    try:
                        salary_min = item.get('salaryMin', 0)
                        salary_max = item.get('salaryMax', 0)
                        salary = f"₹{salary_min//100000}-{salary_max//100000} LPA" if salary_min else "Not specified"
                        jobs.append({
                            "title": item.get('title', 'Unknown'),
                            "company": item.get('company', {}).get('name', 'Unknown'),
                            "salary": salary,
                            "experience": f"{item.get('minExp', 0)}-{item.get('maxExp', 3)} years",
                            "platform": "Cutshort",
                            "url": f"https://cutshort.io/job/{item.get('shortId', '')}",
                            "jd": item.get('description', item.get('title', ''))
                        })
                    except Exception:
                        continue
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"   ⚠️ Cutshort error: {e}")
    print(f"   ✅ Cutshort: Found {len(jobs)} jobs")
    return jobs