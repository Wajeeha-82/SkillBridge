import pandas as pd

df = pd.read_csv("data/jobs.csv")

all_skills = set()

for description in df["description"]:
    skills = [s.strip().lower() for s in description.split(",")]
    for skill in skills:
        if skill:
            all_skills.add(skill)

all_skills = sorted(all_skills)

with open("data/skills.txt", "w") as f:
    for skill in all_skills:
        f.write(skill + "\n")

print(f"Total unique skills found: {len(all_skills)}")
print("skills.txt created successfully!")