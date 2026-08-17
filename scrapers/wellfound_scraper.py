import requests
import time
import random
import json

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://wellfound.com/jobs',
        'x-requested-with': 'XMLHttpRequest'
    }

def scrape_wellfound(keywords, pages=2):
    jobs = []

    for keyword in keywords:
        print(f"   🔍 Wellfound: Searching '{keyword}'...")
        try:
            # Use Wellfound API endpoint
            url = "https://wellfound.com/api/v1/talent/jobs"
            params = {
                'q': keyword,
                'page': 1,
                'remote': 'false',
                'locations[]': 'India'
            }

            response = requests.get(
                url,
                params=params,
                headers=get_headers(),
                timeout=15
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    job_list = data.get('jobs', []) or data.get('data', [])

                    for item in job_list:
                        try:
                            salary_min = item.get('compensation_min', 0)
                            salary_max = item.get('compensation_max', 0)
                            salary = f"${salary_min}k-${salary_max}k" if salary_min else "Not specified"

                            jobs.append({
                                "title": item.get('title', 'Unknown'),
                                "company": item.get('startup', {}).get('name', 'Unknown'),
                                "salary": salary,
                                "experience": f"{item.get('min_experience', 0)}-{item.get('max_experience', 3)} yrs",
                                "platform": "Wellfound",
                                "url": f"https://wellfound.com/jobs/{item.get('id', '')}",
                                "jd": item.get('description', '')[:500]
                            })
                        except:
                            continue
                except:
                    pass

            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"   ⚠️ Wellfound error: {e}")

    print(f"   ✅ Wellfound: Found {len(jobs)} jobs")
    return jobs