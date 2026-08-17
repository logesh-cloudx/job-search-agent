from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import urllib.parse

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def _parse_cards(html):
    jobs = []
    soup = BeautifulSoup(html, 'html.parser')
    for card in soup.find_all('div', class_='srp-card'):
        try:
            title_elem = card.find('h2')
            link_elem = card.find('a', href=True)
            if not title_elem or not link_elem:
                continue

            title = title_elem.get_text(strip=True)

            company_elem = card.select_one('.text-gray-400 span')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"

            loc_elem = card.select_one('i.locations-icon')
            location = loc_elem.parent.get_text(strip=True) if loc_elem else "Not specified"

            exp_elem = card.select_one('i.years-icon')
            experience = exp_elem.parent.get_text(strip=True) if exp_elem else "Not specified"

            salary_elem = card.select_one('i.salary-icon')
            salary_container = salary_elem.find_parent(class_='font-semibold') if salary_elem else None
            salary = salary_container.get_text(strip=True) if salary_container else "Not specified"

            jd_elem = card.find('div', class_='rtd-content')
            jd_text = jd_elem.get_text(' ', strip=True) if jd_elem else title
            jd = f"{jd_text} Location: {location}"

            jobs.append({
                "title": title,
                "company": company,
                "salary": salary,
                "experience": experience,
                "platform": "TimesJobs",
                "url": link_elem.get('href', ''),
                "jd": jd
            })
        except Exception:
            continue
    return jobs


def scrape_timesjobs(keywords):
    """Scrape jobs from TimesJobs. Requires a real browser: the site is a
    client-rendered Next.js app with no server-rendered content or embedded
    JSON, and its TLS cert chain is broken (needs ignore_https_errors)."""
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT, ignore_https_errors=True)

        for keyword in keywords:
            print(f"   🔍 TimesJobs: Searching '{keyword}'...")
            params = {
                'searchType': 'personalizedSearch',
                'txtKeywords': keyword,
            }
            url = "https://www.timesjobs.com/candidate/job-search.html?" + urllib.parse.urlencode(params)

            page = context.new_page()
            try:
                page.goto(url, timeout=25000, wait_until="domcontentloaded")
                page.wait_for_selector('.srp-card', timeout=15000)
                page.wait_for_timeout(1000)
                jobs.extend(_parse_cards(page.content()))
            except Exception as e:
                print(f"   ⚠️ TimesJobs error: {e}")
            finally:
                page.close()

        browser.close()

    print(f"   ✅ TimesJobs: Found {len(jobs)} jobs")
    return jobs
