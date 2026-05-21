import pandas as pd

# Load skills from file
def load_skills():
    with open("data/skills.txt", "r") as f:
        return [line.strip().lower() for line in f if line.strip()]

# Extract matching skills from a job description
def extract_skills(text, skills_list):
    text = text.lower()
    return [skill for skill in skills_list if skill in text]

# Load jobs
df = pd.read_csv("data/jobs.csv")
skills_list = load_skills()

# Apply skill extraction to every job
df["extracted_skills"] = df["description"].apply(lambda x: extract_skills(x, skills_list))
df["skill_count"] = df["extracted_skills"].apply(len)

# Show results
print(df[["job_title", "extracted_skills", "skill_count"]].to_string())