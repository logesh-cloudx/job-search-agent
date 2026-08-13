import requests
import os

def send_job_notification(job, score_result, message):
    """Send job opportunity to Telegram"""

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    score = score_result.get('score', 0)

    if score >= 70:
        emoji = "🟢"
        status = "STRONG MATCH"
    elif score >= 50:
        emoji = "🟡"
        status = "GOOD MATCH"
    else:
        emoji = "🔴"
        status = "WEAK MATCH"

    matching = ', '.join(score_result.get('matching_skills', [])[:5])
    missing = ', '.join(score_result.get('missing_skills', [])[:3])

    text = f"""{emoji} *{status} — {score}% match*

📋 *Role:* {job['title']}
🏢 *Company:* {job['company']}
💰 *Salary:* {job.get('salary', 'Not specified')}
🌐 *Platform:* {job['platform']}
🔗 *Link:* {job['url']}

✅ *Matching Skills:* {matching}
❌ *Missing Skills:* {missing if missing else 'None!'}

📝 *Your Message to Send:*
{message}

---
Reply /apply to mark as applied"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })

    if response.status_code == 200:
        print(f"✅ Telegram notification sent for: {job['title']} at {job['company']}")
    else:
        print(f"❌ Telegram error: {response.text}")


def send_summary(total, applied, skipped):
    """Send daily summary to Telegram"""

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    text = f"""📊 *Job Agent Daily Summary*

📋 Total jobs processed: {total}
✅ Jobs to apply: {applied}
❌ Jobs skipped: {skipped}

Keep applying! Every application counts! 💪"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    })