from groq import Groq
import os
import json

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key)

def generate_application_message(job_title, company, jd_text, profile):
    client = get_client()

    prompt = f"""
You are helping {profile['name']} apply for a job.

JOB DETAILS:
Title: {job_title}
Company: {company}
Job Description: {jd_text[:2000]}

CANDIDATE PROFILE:
Name: {profile['name']}
Experience: {profile['experience_years']} years
Skills: {', '.join(profile['skills'])}
Summary: {profile['summary']}
Key Achievements: {', '.join(profile['achievements'])}
LinkedIn: {profile['linkedin']}
GitHub: {profile['github']}

Write a SHORT personalized application message (max 150 words).
Rules:
- Start with name and experience
- Match 2-3 specific skills from the JD
- Include one achievement with a number
- Mention URBNDOJO live project
- End with contact details
- Sound natural and confident
- No bullet points

Return ONLY the message text, nothing else.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    return response.choices[0].message.content


def score_job_match(job_title, jd_text, profile):
    client = get_client()

    prompt = f"""
Analyze this job and score the match for this candidate.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{jd_text[:2000]}

CANDIDATE SKILLS: {', '.join(profile['skills'])}
CANDIDATE EXPERIENCE: {profile['experience_years']} years
CANDIDATE ROLES: {', '.join(profile['target_roles'])}

Return ONLY this JSON format, nothing else:
{{
    "score": <number 0-100>,
    "matching_skills": ["skill1", "skill2", "skill3"],
    "missing_skills": ["skill1", "skill2"],
    "recommendation": "apply" or "skip",
    "reason": "<one line explanation>",
    "salary_match": "good" or "low" or "unknown"
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    try:
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing score: {e}")
        return {
            "score": 50,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": "apply",
            "reason": "Could not parse",
            "salary_match": "unknown"
        }