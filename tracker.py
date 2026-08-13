import pandas as pd
import os
from datetime import datetime, timedelta

TRACKER_FILE = "job_applications.xlsx"

def load_tracker():
    if os.path.exists(TRACKER_FILE):
        return pd.read_excel(TRACKER_FILE)
    else:
        df = pd.DataFrame(columns=[
            'Date', 'Company', 'Role',
            'Platform', 'URL', 'Salary',
            'Match Score', 'Status',
            'Follow Up Date', 'Notes'
        ])
        df.to_excel(TRACKER_FILE, index=False)
        return df


def add_application(job, score):
    df = load_tracker()

    follow_up = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')

    new_row = {
        'Date': datetime.now().strftime('%Y-%m-%d'),
        'Company': job['company'],
        'Role': job['title'],
        'Platform': job['platform'],
        'URL': job['url'],
        'Salary': job.get('salary', 'NA'),
        'Match Score': score,
        'Status': 'Notified',
        'Follow Up Date': follow_up,
        'Notes': ''
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(TRACKER_FILE, index=False)
    print(f"✅ Tracked: {job['company']} - {job['title']}")


def get_followup_jobs():
    """Get jobs that need follow up today"""
    df = load_tracker()
    today = datetime.now().strftime('%Y-%m-%d')
    followups = df[df['Follow Up Date'] == today]
    return followups