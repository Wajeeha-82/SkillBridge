from flask import Flask, render_template, request, jsonify
import pandas as pd
from collections import Counter

app = Flask(__name__)

# ── Load Data ─────────────────────────────────────────────────────
def load_data():
    return pd.read_csv("data/jobs.csv")

def load_skills():
    with open("data/skills.txt", "r") as f:
        return [line.strip().lower() for line in f
                if line.strip() and len(line.strip()) > 2]

def extract_skills(text, skills_list):
    text = text.lower()
    return [skill for skill in skills_list if skill in text]

def is_relevant_skill(user_skill, required_skills):
    user_clean = user_skill.strip().lower().replace(
        " ", "").replace(".", "").replace("/", "")
    for req in required_skills:
        req_clean = req.strip().lower().replace(
            " ", "").replace(".", "").replace("/", "")
        if user_clean == req_clean:
            return True
        if user_clean in req_clean:
            return True
        if req_clean in user_clean:
            return True
    return False

def get_market_demand(df):
    career_keywords = [
        "Data Analyst", "Data Scientist", "Data Engineer",
        "Frontend Developer", "Full Stack", "Backend Engineer",
        "Digital Marketing", "Graphic Designer", "SEO",
        "Software Engineer", "Machine Learning"
    ]
    career_demand = {}
    for career in career_keywords:
        career_norm = career.lower().replace(" ", "")
        count = len(df[df["job_title"].str.lower().str.replace(
            " ", "", regex=False).str.contains(career_norm)])
        if count > 0:
            career_demand[career] = count
    return dict(sorted(career_demand.items(),
                       key=lambda x: x[1], reverse=True))

def get_skill_demand(career, df, skills_list):
    career_norm = career.lower().replace(" ", "")
    career_jobs = df[df["job_title"].str.lower().str.replace(
        " ", "", regex=False).str.contains(career_norm)]
    if len(career_jobs) == 0:
        return {}, career_jobs
    all_skills = []
    for desc in career_jobs["description"]:
        all_skills.extend(extract_skills(desc, skills_list))
    counter = Counter(all_skills)
    return dict(counter.most_common(25)), career_jobs


# ── Routes ────────────────────────────────────────────────────────
@app.route("/")
def index():
    df            = load_data()
    skills_list   = load_skills()
    market_raw    = get_market_demand(df)
    total_jobs    = len(df)
    total_skills  = len(skills_list)
    total_careers = len(market_raw)

    max_count  = max(market_raw.values()) if market_raw else 1
    market_list = []
    for career, count in market_raw.items():
        market_list.append({
            "career": career,
            "count" : count,
            "pct"   : int((count / max_count) * 100)
        })

    return render_template("index.html",
                           market=market_list,
                           total_jobs=total_jobs,
                           total_skills=total_skills,
                           total_careers=total_careers)


@app.route("/analyze", methods=["POST"])
def analyze():
    data        = request.json
    career_goal = data.get("career", "").strip()
    user_input  = data.get("skills", "").strip()

    if not career_goal or not user_input:
        return jsonify({"error": "Please enter both career goal and skills."})

    df          = load_data()
    skills_list = load_skills()

    user_skills = [s.strip().lower() for s in user_input.split(",")
                   if s.strip()]

    skill_demand, career_jobs = get_skill_demand(
        career_goal, df, skills_list)

    if len(career_jobs) == 0:
        return jsonify({"error": f"No jobs found for '{career_goal}'. "
                        f"Try: Data Analyst, Frontend Developer, "
                        f"Digital Marketing, Graphic Designer"})

    required_skills = list(skill_demand.keys())
    total_jobs      = len(career_jobs)

    # Get ALL skills from career jobs for better matching
    all_career_skills = []
    for desc in career_jobs["description"]:
        all_career_skills.extend(extract_skills(desc, skills_list))
    all_career_skills = list(set(all_career_skills))

    matched    = [s for s in required_skills
                  if is_relevant_skill(s, user_skills)]
    missing    = [s for s in required_skills
                  if not is_relevant_skill(s, user_skills)]

    # Truly irrelevant — not found anywhere in career jobs
    irrelevant = [s for s in user_skills
                  if not is_relevant_skill(s, required_skills)
                  and not is_relevant_skill(s, all_career_skills)]

    # Low demand — exists in career but not top 25
    low_demand = [s for s in user_skills
                  if not is_relevant_skill(s, required_skills)
                  and is_relevant_skill(s, all_career_skills)]

    match_pct  = round((len(matched) / len(required_skills)) * 100, 1)
    gap_pct    = round(100 - match_pct, 1)

    avg_salary = round(career_jobs["salary"].mean())
    min_salary = int(career_jobs["salary"].min())
    max_salary = int(career_jobs["salary"].max())

    location_counts = career_jobs["location"].value_counts().head(5).to_dict()

    missing_with_demand = []
    for skill in missing:
        if skill in skill_demand:
            demand_count = skill_demand[skill]
            demand_pct   = round((demand_count / total_jobs) * 100)
            missing_with_demand.append({
                "skill"       : skill,
                "demand_count": demand_count,
                "demand_pct"  : demand_pct,
                "total_jobs"  : total_jobs
            })
    missing_with_demand.sort(key=lambda x: x["demand_count"], reverse=True)

    return jsonify({
        "career"       : career_goal,
        "total_jobs"   : total_jobs,
        "match_pct"    : match_pct,
        "gap_pct"      : gap_pct,
        "avg_salary"   : avg_salary,
        "min_salary"   : min_salary,
        "max_salary"   : max_salary,
        "matched"      : matched,
        "missing"      : missing,
        "irrelevant"   : irrelevant,
        "low_demand"   : low_demand,
        "locations"    : location_counts,
        "learning_path": missing_with_demand[:8],
        "required"     : required_skills
    })


if __name__ == "__main__":
    app.run(debug=True)