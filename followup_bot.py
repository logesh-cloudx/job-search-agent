import os
import pandas as pd
from datetime import datetime
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

def check_followups():
    """Check and send follow-up reminders"""

    if not os.path.exists(TRACKER_FILE):
        print("No tracker file found!")
        return

    df = pd.read_excel(TRACKER_FILE)
    today = datetime.now().strftime('%Y-%m-%d')

    # Jobs needing follow up today
    due_today = df[
        (df['Follow Up Date'] == today) &
        (df['Status'] == 'Notified')
    ]

    if len(due_today) == 0:
        print("No follow-ups needed today!")
        return

    print(f"📅 {len(due_today)} follow-ups needed today!")

    # Send reminder for each job
    for _, job in due_today.iterrows():
        message = f"""⏰ *Follow-up Reminder!*

📋 *Role:* {job['Role']}
🏢 *Company:* {job['Company']}
🌐 *Platform:* {job['Platform']}
🔗 *Link:* {job['URL']}
📅 *Applied on:* {job['Date']}

*Send this follow-up message:*

Hi,

I applied for the {job['Role']} position at \
{job['Company']} a few days ago and wanted to \
reiterate my strong interest. I have 1.4 years \
of production AWS and DevOps experience and \
believe I would be a great fit for this role.

Would you be available for a quick call this week?

Best regards,
Logesh V
+91 95144 13804
linkedin.com/in/logesh010"""

        send_message(message)
        print(f"✅ Reminder sent: {job['Company']} - {job['Role']}")

    # Update status to "Followed Up"
    df.loc[
        (df['Follow Up Date'] == today) &
        (df['Status'] == 'Notified'),
        'Status'
    ] = 'Followed Up'

    df.to_excel(TRACKER_FILE, index=False)
    print("✅ Tracker updated!")


if __name__ == "__main__":
    check_followups()