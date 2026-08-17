from groq import Groq
import os
import json
from dotenv import load_dotenv

# Load env file explicitly
load_dotenv(dotenv_path="D:\\AI AGENTS\\job agent\\.env")

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file!")
    return Groq(api_key=api_key)

def generate_application_message(job_title, company, jd_text, profile):
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

    try:
        response = get_client().chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            reasoning_effort="low"
        )
    except Exception as e:
        raise RuntimeError(f"Groq API call failed (generate_application_message): {e}")

    return response.choices[0].message.content


def score_job_match(job_title, jd_text, profile):
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

    try:
        response = get_client().chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            reasoning_effort="low"
        )
    except Exception as e:
        raise RuntimeError(f"Groq API call failed (score_job_match): {e}")

    try:
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        print(f"   ⚠️ Score parse error: {e}")
        return {
            "score": 60,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": "apply",
            "reason": "Could not parse",
            "salary_match": "unknown"
        }