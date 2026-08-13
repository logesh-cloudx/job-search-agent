import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

TRACKER_FILE = "job_applications.xlsx"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def generate_weekly_report():
    """Generate and send weekly job search report"""

    if not os.path.exists(TRACKER_FILE):
        send_message("❌ No applications tracked yet!")
        return

    df = pd.read_excel(TRACKER_FILE)

    # Last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    weekly = df[df['Date'] >= week_ago]

    # Stats
    total = len(weekly)
    by_platform = weekly['Platform'].value_counts()
    by_status = weekly['Status'].value_counts()
    avg_score = weekly['Match Score'].mean() if total > 0 else 0

    # Top companies
    top_companies = weekly.nlargest(5, 'Match Score')[
        ['Company', 'Role', 'Match Score']
    ]

    # Build report
    platform_text = "\n".join([
        f"   {platform}: {count} jobs"
        for platform, count in by_platform.items()
    ])

    status_text = "\n".join([
        f"   {status}: {count}"
        for status, count in by_status.items()
    ])

    top_text = "\n".join([
        f"   {row['Company']} — {row['Role']} ({row['Match Score']}%)"
        for _, row in top_companies.iterrows()
    ])

    report = f"""📊 *Weekly Job Search Report*
📅 Week: {week_ago} to {datetime.now().strftime('%Y-%m-%d')}

━━━━━━━━━━━━━━━━━━━━
📈 *Summary*
━━━━━━━━━━━━━━━━━━━━
Total jobs found: {total}
Average match score: {avg_score:.1f}%

━━━━━━━━━━━━━━━━━━━━
🌐 *By Platform*
━━━━━━━━━━━━━━━━━━━━
{platform_text}

━━━━━━━━━━━━━━━━━━━━
📋 *By Status*
━━━━━━━━━━━━━━━━━━━━
{status_text}

━━━━━━━━━━━━━━━━━━━━
⭐ *Top 5 Matches*
━━━━━━━━━━━━━━━━━━━━
{top_text}

━━━━━━━━━━━━━━━━━━━━
💪 Keep applying! Consistency wins!
Target: 10 applications per day
"""

    send_message(report)
    print("✅ Weekly report sent to Telegram!")


if __name__ == "__main__":
    generate_weekly_report()