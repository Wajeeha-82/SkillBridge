from src.career_advisor import career_advisor
import pandas as pd

def load_skills():
    with open("data/skills.txt", "r") as f:
        return [line.strip().lower() for line in f
                if line.strip() and len(line.strip()) > 2]

df          = pd.read_csv("data/jobs.csv")
skills_list = load_skills()

print("=" * 55)
print("      JOB SKILL GAP ANALYZER")
print("      Built with Real Pakistan Job Data")
print("=" * 55)

while True:
    print("\n1. Analyze Career Gap")
    print("2. Exit")
    choice = input("\nChoose > ")

    if choice == "1":
        print("\n🎯 What career do you want?")
        print("   Examples: Data Analyst, Frontend Developer,")
        print("             Digital Marketing, Graphic Designer")
        career_goal = input("\nCareer Goal > ")

        print("\n💼 Enter YOUR current skills (comma separated)")
        print("   Example: python, excel, communication")
        user_input  = input("\nYour Skills > ")
        user_skills = user_input.split(",")

        career_advisor(career_goal, user_skills, df, skills_list)

    elif choice == "2":
        print("\n👋 Goodbye!")
        break
    else:
        print("❌ Invalid choice. Enter 1 or 2.")