import pandas as pd
from collections import Counter

# ── Load skills ───────────────────────────────────────────────────────
def load_skills():
    with open("data/skills.txt", "r") as f:
        # Fix: skip single letter false matches
        return [line.strip().lower() for line in f 
                if line.strip() and len(line.strip()) > 2]

# ── Extract skills from description ──────────────────────────────────
def extract_skills(text, skills_list):
    text = text.lower()
    return [skill for skill in skills_list if skill in text]

# ── Get required skills for a career ─────────────────────────────────
def get_required_skills(career, df, skills_list):
    career_jobs = df[df["job_title"].str.lower().str.contains(career.lower())]

    if len(career_jobs) == 0:
        return [], career_jobs

    all_skills = []
    for desc in career_jobs["description"]:
        all_skills.extend(extract_skills(desc, skills_list))

    counter    = Counter(all_skills)
    top_skills = [skill for skill, count in counter.most_common(15)]

    return top_skills, career_jobs

# ── Main Career Advisor ───────────────────────────────────────────────
def career_advisor(career_goal, user_skills, df, skills_list):
    user_skills = [s.strip().lower() for s in user_skills]

    # Get required skills and matching jobs
    required_skills, career_jobs = get_required_skills(
                                        career_goal, df, skills_list)

    if len(career_jobs) == 0:
        print(f"\n❌ No jobs found for '{career_goal}'.")
        print("Try: Data Analyst, Frontend Developer, Digital Marketing")
        return

    # Calculate gap
    matched   = [s for s in required_skills if s in user_skills]
    missing   = [s for s in required_skills if s not in user_skills]
    match_pct = round((len(matched) / len(required_skills)) * 100, 1)
    gap_pct   = round(100 - match_pct, 1)

    # Salary stats
    avg_salary = round(career_jobs["salary"].mean())
    min_salary = career_jobs["salary"].min()
    max_salary = career_jobs["salary"].max()

    # Demand by city
    location_counts = career_jobs["location"].value_counts()

    # Irrelevant skills warning
    irrelevant = [s for s in user_skills if s not in required_skills]

    # ── Print Report ──────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print(f"   CAREER REPORT: {career_goal.upper()}")
    print("=" * 55)

    print(f"\n📊 Total Jobs Found   : {len(career_jobs)}")
    print(f"💰 Salary Range       : {min_salary:,} – {max_salary:,} PKR")
    print(f"💵 Average Salary     : {avg_salary:,} PKR")

    print(f"\n📍 Market Demand by City:")
    for loc, count in location_counts.head(4).items():
        bar = "█" * count
        print(f"   {loc:<15} {bar} ({count} jobs)")

    print(f"\n🎯 Top Required Skills:")
    print(f"   {', '.join(required_skills)}")

    print(f"\n✅ Your Matched Skills ({len(matched)}/{len(required_skills)}):")
    if matched:
        print(f"   {', '.join(matched)}")
    else:
        print("   None — Start learning now!")

    print(f"\n❌ Missing Skills ({len(missing)}):")
    if missing:
        print(f"   {', '.join(missing)}")
    else:
        print("   None — You are fully ready!")

    print(f"\n📈 Match Score        : {match_pct}%")
    print(f"📉 Skill Gap          : {gap_pct}%")

    # Irrelevant skills warning
    if irrelevant:
        print(f"\n⚠️  WARNING — Irrelevant Skills Detected:")
        print(f"   You know: {', '.join(irrelevant)}")
        print(f"   These are NOT required for {career_goal}!")
        print(f"   👉 Stop wasting time — focus on missing skills!")

    # Learning path
    print(f"\n🛣️  Suggested Learning Path:")
    for i, skill in enumerate(missing[:5], 1):
        print(f"   Step {i}: Learn  →  {skill}")

    print(f"\n💡 Tip: Master top 5 missing skills to become job-ready!")
    print("=" * 55)


