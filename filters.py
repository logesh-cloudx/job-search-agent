import re

def filter_by_salary(job, min_lpa=4, max_lpa=12):
    salary = job.get('salary', '').lower()
    if salary in ['not specified', 'na', '', 'not disclosed']:
        return True
    numbers = re.findall(r'\d+\.?\d*', salary)
    if not numbers:
        return True
    try:
        amounts = [float(n) for n in numbers]
        if 'month' in salary or '/mo' in salary:
            amounts = [a * 12 / 100000 for a in amounts]
        max_salary = max(amounts)
        min_salary = min(amounts)
        if max_salary < min_lpa:
            return False
        if min_salary > max_lpa:
            return False
        return True
    except Exception:
        return True

def filter_by_experience(job, min_years=0, max_years=3):
    exp = job.get('experience', '').lower()
    title = job.get('title', '').lower()
    senior_keywords = [
        'senior', 'lead', 'principal', 'staff',
        'manager', 'director', 'head of', 'vp',
        'architect', '5+ years', '7+ years',
        '8+ years', '10+ years'
    ]
    for keyword in senior_keywords:
        if keyword in title or keyword in exp:
            return False
    return True

def apply_all_filters(jobs, min_lpa=4, max_lpa=12,
                      min_exp=0, max_exp=3):
    filtered = []
    for job in jobs:
        if not filter_by_salary(job, min_lpa, max_lpa):
            continue
        if not filter_by_experience(job, min_exp, max_exp):
            continue
        filtered.append(job)
    print(f"After filtering: {len(filtered)} jobs (from {len(jobs)})")
    return filtered
