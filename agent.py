import os
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from profile import MY_PROFILE
from message_generator import generate_application_message, score_job_match
from telegram_notifier import send_job_notification, send_summary
from tracker import add_application, get_followup_jobs
from scrapers.naukri_scraper import scrape_naukri
from scrapers.indeed_scraper import scrape_indeed
from scrapers.linkedin_scraper import scrape_linkedin
from scrapers.instahyre_scraper import scrape_instahyre
from scrapers.shine_scraper import scrape_shine
from scrapers.wellfound_scraper import scrape_wellfound
from scrapers.glassdoor_scraper import scrape_glassdoor
from scrapers.timesjobs_scraper import scrape_timesjobs
from scrapers.foundit_scraper import scrape_foundit
from scrapers.cutshort_scraper import scrape_cutshort
from scrapers.hirist_scraper import scrape_hirist
from scrapers.remote_scraper import scrape_remote
from scrapers.company_scraper import scrape_company_jobs
from filters import apply_all_filters

load_dotenv()

SEARCH_KEYWORDS = [
    "DevOps Engineer",
    "Cloud Engineer",
    "AWS Engineer",
    "Linux Administrator",
    "Cloud Operations Engineer",
    "Infrastructure Engineer",
    "Site Reliability Engineer"
]

SEARCH_LOCATION = "India"
MIN_MATCH_SCORE = 60
MAX_JOBS_PER_RUN = 50


def scrape_all_portals():
    print("\n🌐 Scraping all 13 job portals simultaneously...")
    print("=" * 50)

    all_jobs = []

    with ThreadPoolExecutor(max_workers=13) as executor:
        futures = {
            executor.submit(scrape_naukri, SEARCH_KEYWORDS): "Naukri",
            executor.submit(scrape_indeed, SEARCH_KEYWORDS): "Indeed",
            executor.submit(scrape_linkedin, SEARCH_KEYWORDS): "LinkedIn",
            executor.submit(scrape_instahyre, SEARCH_KEYWORDS): "Instahyre",
            executor.submit(scrape_shine, SEARCH_KEYWORDS): "Shine",
            executor.submit(scrape_wellfound, SEARCH_KEYWORDS): "Wellfound",
            executor.submit(scrape_glassdoor, SEARCH_KEYWORDS): "Glassdoor",
            executor.submit(scrape_timesjobs, SEARCH_KEYWORDS): "TimesJobs",
            executor.submit(scrape_foundit, SEARCH_KEYWORDS): "Foundit",
            executor.submit(scrape_cutshort, SEARCH_KEYWORDS): "Cutshort",
            executor.submit(scrape_hirist, SEARCH_KEYWORDS): "Hirist",
            executor.submit(scrape_remote, SEARCH_KEYWORDS): "Remote.co",
            executor.submit(scrape_company_jobs, SEARCH_KEYWORDS): "Company Direct",
        }

        for future in as_completed(futures):
            portal = futures[future]
            try:
                jobs = future.result()
                all_jobs.extend(jobs)
                print(f"✅ {portal}: {len(jobs)} jobs collected")
            except Exception as e:
                print(f"❌ {portal} failed: {e}")

    print(f"\n📊 Total jobs found: {len(all_jobs)}")
    return all_jobs


def remove_duplicates(jobs):
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    print(f"🔄 After removing duplicates: {len(unique_jobs)} unique jobs")
    return unique_jobs


def process_jobs(jobs):
    print("\n🤖 AI Scoring all jobs...")
    print("=" * 50)

    applied_count = 0
    skipped_count = 0
    jobs_to_process = jobs[:MAX_JOBS_PER_RUN]

    for i, job in enumerate(jobs_to_process, 1):
        print(f"\n[{i}/{len(jobs_to_process)}] "
              f"{job['title']} at {job['company']}")
        try:
            score_result = score_job_match(
                job['title'],
                job['jd'],
                MY_PROFILE
            )
            score = score_result.get('score', 0)
            recommendation = score_result.get('recommendation', 'skip')
            print(f"   Score: {score}% | {recommendation}")

            if score < MIN_MATCH_SCORE or recommendation == 'skip':
                print(f"   ❌ Skipped")
                skipped_count += 1
                continue

            message = generate_application_message(
                job['title'],
                job['company'],
                job['jd'],
                MY_PROFILE
            )

            send_job_notification(job, score_result, message)
            add_application(job, score)
            applied_count += 1
            print(f"   ✅ Sent to Telegram!")
            time.sleep(0.5)

        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            continue

    return applied_count, skipped_count


def check_followups():
    print("\n📅 Checking follow-ups for today...")
    followups = get_followup_jobs()
    if len(followups) == 0:
        print("   No follow-ups needed today!")
        return
    print(f"   {len(followups)} follow-ups needed:")
    for _, job in followups.iterrows():
        print(f"   📨 {job['Company']} - {job['Role']}")


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 JOB SEARCH AGENT v5.0")
    print("=" * 50)
    print(f"🎯 Keywords: {', '.join(SEARCH_KEYWORDS[:3])}...")
    print(f"📍 Location: {SEARCH_LOCATION}")
    print(f"📊 Min match score: {MIN_MATCH_SCORE}%")

    min_lpa = float(os.getenv("MIN_SALARY_LPA", 4))
    max_lpa = float(os.getenv("MAX_SALARY_LPA", 12))
    min_exp = float(os.getenv("MIN_EXPERIENCE_YEARS", 0))
    max_exp = float(os.getenv("MAX_EXPERIENCE_YEARS", 3))

    print(f"💰 Salary: ₹{min_lpa}L - ₹{max_lpa}L")
    print(f"👨‍💼 Experience: {min_exp} - {max_exp} years")
    print(f"🌐 Portals: 13 portals!")

    all_jobs = scrape_all_portals()
    unique_jobs = remove_duplicates(all_jobs)
    unique_jobs = apply_all_filters(
        unique_jobs, min_lpa, max_lpa, min_exp, max_exp
    )

    applied, skipped = process_jobs(unique_jobs)
    send_summary(len(unique_jobs), applied, skipped)
    check_followups()

    print("\n" + "=" * 50)
    print("🤖 JOB SEARCH AGENT v5.0 completed!")
    print(f"✅ Jobs sent to Telegram: {applied}")
    print(f"❌ Jobs skipped: {skipped}")
    print("=" * 50)