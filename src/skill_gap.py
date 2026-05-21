import pandas as pd
from collections import Counter

# ── Load skills list ──────────────────────────────────────────────────
def load_skills():
    with open("data/skills.txt", "r") as f:
        return [line.strip().lower() for line in f if line.strip()]

# ── Extract skills from one job description ───────────────────────────
def extract_skills(text, skills_list):
    text = text.lower()
    return [skill for skill in skills_list if skill in text]

# ── Get top required skills for a career ─────────────────────────────
def get_required_skills(career, df, skills_list):
    # Filter jobs matching career goal
    career_jobs = df[df["job_title"].str.lower().str.contains(career.lower())]

    if len(career_jobs) == 0:
        return [], career_jobs

    # Collect all skills from all matching jobs
    all_skills = []
    for desc in career_jobs["description"]:
        all_skills.extend(extract_skills(desc, skills_list))

    # Count frequency of each skill
    counter = Counter(all_skills)

    # Return top 15 most demanded skills
    top_skills = [skill for skill, count in counter.most_common(15)]

    return top_skills, career_jobs

# ── Calculate skill gap ───────────────────────────────────────────────
def calculate_gap(user_skills, required_skills):
    user_skills = [s.strip().lower() for s in user_skills]

    matched  = [s for s in required_skills if s in user_skills]
    missing  = [s for s in required_skills if s not in user_skills]
    match_pct = round((len(matched) / len(required_skills)) * 100, 1)
    gap_pct   = round(100 - match_pct, 1)

    return matched, missing, match_pct, gap_pct

# ── Test it ───────────────────────────────────────────────────────────
df          = pd.read_csv("data/jobs.csv")
skills_list = load_skills()

career      = "Data Analyst"
user_skills = ["excel", "communication"]

required_skills, career_jobs = get_required_skills(career, df, skills_list)
matched, missing, match_pct, gap_pct = calculate_gap(user_skills, required_skills)

print(f"Career         : {career}")
print(f"Jobs Found     : {len(career_jobs)}")
print(f"Required Skills: {required_skills}")
print(f"Your Skills    : {user_skills}")
print(f"Matched        : {matched}")
print(f"Missing        : {missing}")
print(f"Match Score    : {match_pct}%")
print(f"Skill Gap      : {gap_pct}%")