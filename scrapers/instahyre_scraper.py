import requests
import fake_useragent
import time

def scrape_instahyre(keywords):
    """Scrape jobs from Instahyre"""
    
    ua = fake_useragent.UserAgent()
    jobs = []
    
    for keyword in keywords:
        print(f"   🔍 Instahyre: Searching '{keyword}'...")
        
        try:
            url = "https://www.instahyre.com/api/v1/opportunity/"
            
            params = {
                'search': keyword,
                'limit': 20,
                'offset': 0
            }
            
            headers = {
                'User-Agent': ua.random,
                'Accept': 'application/json',
                'Referer': 'https://www.instahyre.com/jobs'
            }
            
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for item in results:
                    try:
                        job = {
                            "title": item.get('designation', 'Unknown'),
                            "company": item.get('employer', {}).get('name', 'Unknown'),
                            "salary": f"{item.get('min_salary', 'NA')} - {item.get('max_salary', 'NA')} LPA",
                            "platform": "Instahyre",
                            "url": f"https://www.instahyre.com/jobs/{item.get('id', '')}",
                            "jd": item.get('description', item.get('designation', ''))
                        }
                        jobs.append(job)
                    except:
                        continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ⚠️ Instahyre error: {e}")
    
    print(f"   ✅ Instahyre: Found {len(jobs)} jobs")
    return jobs